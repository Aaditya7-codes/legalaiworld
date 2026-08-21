#!/usr/bin/env python3
"""Turn an existing article directory into a redirect stub pointing at a
stronger sibling article covering the same topic (keyword-cannibalization
cleanup). Keeps the URL alive (meta-refresh + canonical) instead of
deleting it, in case it has external backlinks or direct traffic.

Usage: python3 scripts/make_redirect.py <old-slug> <new-slug> <old-title> <new-title>
"""
from __future__ import annotations

import sys
from pathlib import Path

SITE = "https://legalaiworld.com"
ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{old_title} - LegalAIWorld</title>
<meta name="description" content="This article has been merged into a newer, more complete guide: {new_title}.">
<link rel="canonical" href="{new_url}">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={new_url}">
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
<h1>This article has moved</h1>
<div class="meta"><span class="eyebrow">Updated</span> &middot; 2026-08-21</div>
<div class="entry-content">
<p>"{old_title}" has been merged into a newer, more complete guide covering the same tools:</p>
<p><a href="{new_url}"><strong>{new_title} &rarr;</strong></a></p>
<p>You're being redirected automatically. If nothing happens, use the link above.</p>
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
    old_slug, new_slug, old_title, new_title = sys.argv[1:5]
    new_url = f"{SITE}/{new_slug}/"
    out = TEMPLATE.format(old_title=old_title, new_title=new_title, new_url=new_url)
    out_path = ROOT / old_slug / "index.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote redirect stub: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
