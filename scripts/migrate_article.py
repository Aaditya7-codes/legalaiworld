#!/usr/bin/env python3
"""Fetch a live LegalAIWorld WordPress article and emit a static HTML page.

Preserves the exact slug/URL, meta description, canonical, OG tags, and
Article JSON-LD so the migration does not reset search rankings.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup
from PIL import Image

SITE = "https://legalaiworld.com"
ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - LegalAIWorld</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="LegalAIWorld">
<meta property="og:type" content="article">
<meta property="og:title" content="{title} - LegalAIWorld">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&amp;display=swap">
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<header class="masthead">
<div class="container">
<a class="brand" href="/"><img src="/assets/logo.svg" alt=""><span>LegalAIWorld</span></a>
<nav class="main-nav"></nav>
</div>
</header>

<main class="article">
<div class="article-container">
<h1>{title}</h1>
<div class="meta"><span class="eyebrow">{category}</span> &middot; {date}</div>
{featured_image}
{disclosure}
<div class="entry-content">
{content}
</div>
</div>
</main>

<footer class="footer">
<div class="container">
<div class="footer-links">
<a href="/about-us/">About</a>
<a href="/disclaimer/">Disclaimer</a>
<a href="/affiliate-disclosure/">Affiliate Disclosure</a>
<a href="/terms-of-use/">Terms of Use</a>
<a href="/privacy-policy/">Privacy Policy</a>
</div>
<div class="footer-bottom">
<span>&copy; <span data-current-year></span> LegalAIWorld</span>
</div>
</div>
</footer>
<script src="/assets/site.js"></script>
</body>
</html>
"""

AFFILIATE_NOTE = (
    '<div class="disclosure-note">Some links in this article are affiliate links. '
    'If you buy through them, we may earn a commission at no extra cost to you. '
    'See our <a href="/affiliate-disclosure/">Affiliate Disclosure</a> for details.</div>'
)


def fetch(slug: str) -> tuple[dict, str]:
    from urllib.parse import quote

    api_url = f"{SITE}/wp-json/wp/v2/posts?slug={quote(slug)}"
    with urlopen(api_url, timeout=30) as resp:
        posts = json.loads(resp.read())
    if not posts:
        raise SystemExit(f"No post found for slug: {slug}")
    post = posts[0]

    page_url = f"{SITE}/{quote(slug)}/"
    with urlopen(page_url, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    return post, html


FALLBACK_IMAGE_NAME = "cropped-Screenshot-2025-08-15-at-4.15.25-PM.png"
IMAGES_DIR = ROOT / "assets" / "images"
MAX_IMAGE_WIDTH = 1200
JPEG_QUALITY = 84


def localize_image(url: str) -> str:
    """Download a wp-content image (if not already local), resize it to
    a max width and re-encode as JPEG for page speed, and return the
    self-hosted URL. Leaves non-wp-content URLs untouched."""
    if "/wp-content/uploads/" not in url:
        return url
    filename = url.rsplit("/", 1)[-1]
    if filename == FALLBACK_IMAGE_NAME:
        return f"{SITE}/assets/social-fallback.png"
    jpg_name = Path(filename).with_suffix(".jpg").name
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    local_path = IMAGES_DIR / jpg_name
    if not local_path.exists():
        with urlopen(url, timeout=30) as resp:
            raw = resp.read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = im.size
        if w > MAX_IMAGE_WIDTH:
            h = round(h * MAX_IMAGE_WIDTH / w)
            w = MAX_IMAGE_WIDTH
            im = im.resize((w, h), Image.LANCZOS)
        im.save(local_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return f"{SITE}/assets/images/{jpg_name}"


def image_dimensions(url: str) -> tuple[int, int] | None:
    """Read back the actual (possibly resized) dimensions of a localized
    image, so JSON-LD width/height can be kept in sync."""
    if "/assets/images/" not in url:
        return None
    local_path = IMAGES_DIR / url.rsplit("/", 1)[-1]
    if not local_path.exists():
        return None
    with Image.open(local_path) as im:
        return im.size


def extract(post: dict, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    head = html.split("</head>")[0]

    desc_match = re.search(r'<meta name="description" content="([^"]*)"', head)
    description = desc_match.group(1) if desc_match else ""

    canon_match = re.search(r'<link rel="canonical" href="([^"]*)"', head)
    canonical = canon_match.group(1) if canon_match else f"{SITE}/{post['slug']}/"

    # The real per-article featured image lives in .entry-header's post
    # thumbnail, not the <meta og:image> tag -- AIOSEO's og:image often
    # falls back to the site logo even when a real featured image is set,
    # so og:image alone is not a reliable source.
    thumb_img = soup.select_one(".entry-header .post-thumb-img-content img")
    if thumb_img and thumb_img.get("src"):
        raw_image = re.sub(r"-\d+x\d+(?=\.\w+$)", "", thumb_img["src"])  # strip WP size suffix
    else:
        og_image_match = re.search(r'<meta property="og:image" content="([^"]*)"', head)
        raw_image = og_image_match.group(1) if og_image_match else ""
    is_fallback = (not raw_image) or raw_image.rsplit("/", 1)[-1] == FALLBACK_IMAGE_NAME
    image = localize_image(raw_image) if raw_image else ""

    ld_match = re.search(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    )
    jsonld_raw = ld_match.group(1).strip() if ld_match else "{}"
    # Rewrite any wp-content image URLs embedded in the JSON-LD (escaped-slash form)
    for wp_url in set(re.findall(r'https:\\/\\/legalaiworld\.com\\/wp-content\\/uploads\\/[^"\s]*?\.(?:png|jpg|jpeg|webp|gif)', jsonld_raw)):
        localized = localize_image(wp_url.replace("\\/", "/"))
        dims = image_dimensions(localized)
        jsonld_raw = jsonld_raw.replace(wp_url, localized.replace("/", "\\/"))
        if dims:
            w, h = dims
            fname_escaped = re.escape(localized.rsplit("/", 1)[-1])
            jsonld_raw = re.sub(
                rf'({fname_escaped}"(?:,"@id":"[^"]*")?,"width":)\d+(,"height":)\d+',
                rf"\g<1>{w}\g<2>{h}",
                jsonld_raw,
            )

    content_el = soup.find(class_="entry-content")
    content_html = str(content_el) if content_el else ""
    # strip the outer wrapper div, keep inner HTML only
    inner = re.sub(r'^<div[^>]*>', '', content_html)
    inner = re.sub(r'</div>$', '', inner.strip())

    category = "AI Tools"
    if post.get("categories"):
        cat_map = {16: "AI Tools", 17: "Legal Research", 18: "Compliance", 1: "Uncategorized"}
        category = cat_map.get(post["categories"][0], "AI Tools")

    return {
        "title": post["title"]["rendered"],
        "slug": post["slug"],
        "description": description.replace('"', "&quot;"),
        "canonical": canonical,
        "image": image,
        "is_fallback": is_fallback,
        "jsonld": jsonld_raw,
        "content": inner,
        "category": category,
        "date": post["date"][:10],
    }


def render(data: dict, affiliate: bool) -> str:
    featured_image = ""
    if data["image"] and not data["is_fallback"]:
        # Root-relative so it resolves under any host (local preview or
        # production); og:image/JSON-LD keep the absolute SITE URL since
        # those are read by external crawlers, not the browser.
        image_path = data["image"].replace(SITE, "", 1)
        featured_image = (
            f'<img class="featured-image" src="{image_path}" '
            f'alt="{data["title"]}" loading="lazy">'
        )
    return TEMPLATE.format(
        title=data["title"],
        description=data["description"],
        canonical=data["canonical"],
        image=data["image"],
        jsonld=data["jsonld"],
        content=data["content"],
        category=data["category"],
        date=data["date"],
        featured_image=featured_image,
        disclosure=AFFILIATE_NOTE if affiliate else "",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--affiliate", action="store_true", help="Include affiliate disclosure note")
    args = parser.parse_args()

    post, html = fetch(args.slug)
    data = extract(post, html)
    output = render(data, args.affiliate)

    out_dir = ROOT / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(output, encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
