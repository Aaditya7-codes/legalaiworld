#!/usr/bin/env python3
"""Fetch a live LegalAIWorld WordPress static page and emit a static HTML page."""
from __future__ import annotations

import argparse
import re
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
<link rel="stylesheet" href="/assets/styles.css">
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    args = parser.parse_args()
    slug = args.slug

    page_url = f"{SITE}/{slug}/"
    with urlopen(page_url, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    head = html.split("</head>")[0]
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', head)
    description = (desc_match.group(1) if desc_match else "").replace('"', "&quot;")
    canon_match = re.search(r'<link rel="canonical" href="([^"]*)"', head)
    canonical = canon_match.group(1) if canon_match else f"{SITE}/{slug}/"

    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else slug.replace("-", " ").title()

    content_el = soup.find(class_="entry-content")
    content_html = str(content_el) if content_el else ""
    inner = re.sub(r"^<div[^>]*>", "", content_html)
    inner = re.sub(r"</div>$", "", inner.strip())

    output = TEMPLATE.format(
        title=title, description=description, canonical=canonical, content=inner
    )

    out_dir = ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(output, encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
