#!/usr/bin/env python3
"""Fetch a live LegalAIWorld WordPress article and emit a static HTML page.

Preserves the exact slug/URL, meta description, canonical, OG tags, and
Article JSON-LD so the migration does not reset search rankings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup

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
    api_url = f"{SITE}/wp-json/wp/v2/posts?slug={slug}"
    with urlopen(api_url, timeout=30) as resp:
        posts = json.loads(resp.read())
    if not posts:
        raise SystemExit(f"No post found for slug: {slug}")
    post = posts[0]

    page_url = f"{SITE}/{slug}/"
    with urlopen(page_url, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    return post, html


def extract(post: dict, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    head = html.split("</head>")[0]

    desc_match = re.search(r'<meta name="description" content="([^"]*)"', head)
    description = desc_match.group(1) if desc_match else ""

    canon_match = re.search(r'<link rel="canonical" href="([^"]*)"', head)
    canonical = canon_match.group(1) if canon_match else f"{SITE}/{post['slug']}/"

    og_image_match = re.search(r'<meta property="og:image" content="([^"]*)"', head)
    image = og_image_match.group(1) if og_image_match else ""

    ld_match = re.search(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    )
    jsonld_raw = ld_match.group(1).strip() if ld_match else "{}"

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
        "jsonld": jsonld_raw,
        "content": inner,
        "category": category,
        "date": post["date"][:10],
    }


def render(data: dict, affiliate: bool) -> str:
    return TEMPLATE.format(
        title=data["title"],
        description=data["description"],
        canonical=data["canonical"],
        image=data["image"],
        jsonld=data["jsonld"],
        content=data["content"],
        category=data["category"],
        date=data["date"],
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
