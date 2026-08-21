#!/usr/bin/env python3
"""Author a brand-new (non-WordPress-sourced) article as a static page.

Unlike migrate_article.py, there's no WordPress post to pull JSON-LD from,
so this hand-builds the same AIOSEO-style @graph (BlogPosting,
BreadcrumbList, Organization, Person, WebPage, WebSite) that
audit_site.py and every migrated page already expect. Uses the fallback
social-fallback.png image pattern (matches how migrated articles with no
real featured image render) until a real hero image is generated.

Usage: import and call write_article(...) from a small per-article driver,
or run standalone with a JSON spec:
    python3 scripts/new_article.py spec.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://legalaiworld.com"
ROOT = Path(__file__).resolve().parents[1]
AUTHOR_URL = f"{SITE}/author/sharma-aditya177gmail-com/"
GRAVATAR = "https://secure.gravatar.com/avatar/8dc59744f995fb0faa50eb6c7fe24dbdb5a57f45cc94007da40166f04c1977f3?s=96&d=mm&r=g"
FALLBACK_IMAGE = f"{SITE}/assets/social-fallback.png"

CATEGORY_SLUGS = {
    "AI Tools": "ai-tools",
    "Legal Research": "legal-research",
    "Compliance": "compliance",
    "Uncategorized": "uncategorized",
}

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
<meta property="og:image" content="{og_image}">
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
<div class="meta"><span class="eyebrow">{category}</span> &middot; {date}{updated}</div>
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


def _breadcrumb(slug: str, title: str, category: str) -> dict:
    cat_slug = CATEGORY_SLUGS[category]
    cat_url = f"{SITE}/category/{cat_slug}/"
    page_url = f"{SITE}/{slug}/"
    return {
        "@type": "BreadcrumbList",
        "@id": f"{page_url}#breadcrumblist",
        "itemListElement": [
            {
                "@type": "ListItem",
                "@id": f"{SITE}#listItem",
                "position": 1,
                "name": "Home",
                "item": SITE,
                "nextItem": {"@type": "ListItem", "@id": f"{cat_url}#listItem", "name": category},
            },
            {
                "@type": "ListItem",
                "@id": f"{cat_url}#listItem",
                "position": 2,
                "name": category,
                "item": cat_url,
                "nextItem": {"@type": "ListItem", "@id": f"{page_url}#listItem", "name": title},
                "previousItem": {"@type": "ListItem", "@id": f"{SITE}#listItem", "name": "Home"},
            },
            {
                "@type": "ListItem",
                "@id": f"{page_url}#listItem",
                "position": 3,
                "name": title,
                "previousItem": {"@type": "ListItem", "@id": f"{cat_url}#listItem", "name": category},
            },
        ],
    }


def build_jsonld(
    *, slug: str, title: str, description: str, category: str, date_iso: str,
    image_url: str | None, image_w: int | None, image_h: int | None,
    date_modified_iso: str | None = None,
) -> str:
    # A refreshed article keeps its original datePublished (that's the URL's
    # ranking history) but advertises a new dateModified.
    mod_iso = date_modified_iso or date_iso
    page_url = f"{SITE}/{slug}/"
    author_ref = {"@id": f"{AUTHOR_URL}#author"}
    org_ref = {"@id": f"{SITE}/#organization"}

    if image_url:
        blogposting_image = {"@type": "ImageObject", "url": image_url, "width": image_w, "height": image_h}
        webpage_image = {
            "@type": "ImageObject", "url": image_url,
            "@id": f"{page_url}#mainImage", "width": image_w, "height": image_h,
        }
        webpage_extra = {
            "image": {"@id": f"{page_url}#mainImage"},
            "primaryImageOfPage": {"@id": f"{page_url}#mainImage"},
        }
    else:
        blogposting_image = {
            "@type": "ImageObject", "url": FALLBACK_IMAGE,
            "@id": f"{SITE}/#articleImage", "width": 740, "height": 247,
        }
        webpage_extra = {}

    blogposting = {
        "@type": "BlogPosting",
        "@id": f"{page_url}#blogposting",
        "name": f"{title} - LegalAIWorld",
        "headline": title,
        "author": author_ref,
        "publisher": org_ref,
        "image": blogposting_image,
        "datePublished": date_iso,
        "dateModified": mod_iso,
        "inLanguage": "en-US",
        "mainEntityOfPage": {"@id": f"{page_url}#webpage"},
        "isPartOf": {"@id": f"{page_url}#webpage"},
        "articleSection": category,
    }

    organization = {
        "@type": "Organization",
        "@id": f"{SITE}/#organization",
        "name": "LegalAIWorld",
        "description": "Your Guide to AI in Law",
        "url": f"{SITE}/",
        "telephone": "+918884331688",
        "logo": {
            "@type": "ImageObject", "url": FALLBACK_IMAGE,
            "@id": f"{page_url}#organizationLogo", "width": 740, "height": 247,
        },
        "image": {"@id": f"{page_url}#organizationLogo"},
    }

    person = {
        "@type": "Person",
        "@id": f"{AUTHOR_URL}#author",
        "url": AUTHOR_URL,
        "name": "Admin",
        "image": {
            "@type": "ImageObject", "@id": f"{page_url}#authorImage",
            "url": GRAVATAR, "width": 96, "height": 96, "caption": "Admin",
        },
    }

    webpage = {
        "@type": "WebPage",
        "@id": f"{page_url}#webpage",
        "url": page_url,
        "name": f"{title} - LegalAIWorld",
        "description": description,
        "inLanguage": "en-US",
        "isPartOf": {"@id": f"{SITE}/#website"},
        "breadcrumb": {"@id": f"{page_url}#breadcrumblist"},
        "author": author_ref,
        "creator": author_ref,
        **webpage_extra,
        "datePublished": date_iso,
        "dateModified": mod_iso,
    }

    website = {
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "url": f"{SITE}/",
        "name": "LegalAIWorld",
        "description": "Your Guide to AI in Law",
        "inLanguage": "en-US",
        "publisher": org_ref,
    }

    graph = [blogposting, _breadcrumb(slug, title, category), organization, person, webpage, website]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=True, separators=(",", ":"))


def write_article(
    *, slug: str, title: str, description: str, category: str, date: str,
    content_html: str, affiliate: bool = False,
    image_filename: str | None = None,
    date_modified: str | None = None,
) -> Path:
    date_iso = f"{date}T09:00:00+00:00"
    date_modified_iso = f"{date_modified}T09:00:00+00:00" if date_modified else None
    image_url = image_w = image_h = None
    featured_image_tag = ""
    og_image = FALLBACK_IMAGE

    if image_filename:
        from PIL import Image
        local_path = ROOT / "assets" / "images" / image_filename
        with Image.open(local_path) as im:
            image_w, image_h = im.size
        image_url = f"{SITE}/assets/images/{image_filename}"
        og_image = image_url
        featured_image_tag = (
            f'<img class="featured-image" src="/assets/images/{image_filename}" '
            f'alt="{title}" loading="lazy">'
        )

    jsonld = build_jsonld(
        slug=slug, title=title, description=description, category=category,
        date_iso=date_iso, image_url=image_url, image_w=image_w, image_h=image_h,
        date_modified_iso=date_modified_iso,
    )

    # Show the refresh date in the byline too -- a reader skimming a
    # "best tools in <year>" page judges freshness before reading a word.
    updated = f" &middot; Updated {date_modified}" if date_modified else ""

    page = TEMPLATE.format(
        title=title,
        updated=updated,
        description=description.replace('"', "&quot;"),
        canonical=f"{SITE}/{slug}/",
        og_image=og_image,
        jsonld=jsonld,
        content=content_html,
        category=category,
        date=date,
        featured_image=featured_image_tag,
        disclosure=AFFILIATE_NOTE if affiliate else "",
    )

    out_dir = ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(page, encoding="utf-8")
    return out_path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: new_article.py spec.json", file=sys.stderr)
        return 1
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    content_html = Path(spec.pop("content_file")).read_text(encoding="utf-8")
    out = write_article(content_html=content_html, **spec)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
