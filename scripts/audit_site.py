#!/usr/bin/env python3
"""Lightweight static integrity checks for the published site.

Adapted from pickleballcosmos's audit_site.py. The main structural
difference here: JSON-LD is WordPress/AIOSEO's @graph format with a
BlogPosting node, not a flat Article object, so the schema check walks
the graph looking for that node instead of checking the top level.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://legalaiworld.com"
EXCLUDE_DIRS = {"assets", "scripts", ".git"}
# Redirect stubs: pages retired in favor of a stronger sibling article
# covering the same topic (keyword cannibalization cleanup). These keep
# their directory (so old links/bookmarks still resolve via meta-refresh
# + canonical) but are excluded from full article-page checks and the
# sitemap, since they're not meant to be indexed as separate pages.
EXCLUDE_ROUTES: set[str] = {
    "/7-best-ai-tools-for-contract-review-lawyers-in-2025/",
    "/7-best-legal-ai-chatbots-for-lawyers-in-september-2025-reviewed/",
}
SCRIPT_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
URL_RE = re.compile(r'(?:href|src)=["\']([^"\']+)["\']')
REQUIRED_BLOGPOSTING_KEYS = ("author", "image", "publisher", "articleSection")


def normalize(path: str) -> str:
    path = path.split("#", 1)[0].split("?", 1)[0]
    return path if path.endswith(("/", ".html")) else path + "/"


def route_for(page: Path) -> str:
    relative = page.relative_to(ROOT)
    if relative.parent == Path("."):
        return "/"
    return f"/{relative.parent.as_posix()}/"


def local_target_exists(page: Path, reference: str) -> bool:
    parts = urlsplit(reference)
    if parts.scheme or parts.netloc or reference.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return True
    target = unquote(parts.path)
    if not target:
        return True
    candidate = ROOT / target.lstrip("/") if target.startswith("/") else page.parent / target
    candidates = [candidate]
    if target.endswith("/"):
        candidates.append(candidate / "index.html")
    elif not candidate.suffix:
        candidates.extend((candidate / "index.html", candidate.with_suffix(".html")))
    return any(item.is_file() for item in candidates)


def is_article_page(page: Path) -> bool:
    """Articles live at repo root (not under assets/scripts/category/legal pages)."""
    top = page.relative_to(ROOT).parts[0]
    legal_and_special = {
        "assets", "scripts", "category", "about-us", "disclaimer",
        "affiliate-disclosure", "terms-of-use", "privacy-policy",
    }
    return top not in legal_and_special and page != ROOT / "index.html"


def main() -> int:
    all_pages = [
        p for p in ROOT.rglob("index.html")
        if p.relative_to(ROOT).parts[0] not in EXCLUDE_DIRS and route_for(p) not in EXCLUDE_ROUTES
    ]

    sitemap_path = ROOT / "sitemap.xml"
    urls = re.findall(rf"<loc>{re.escape(SITE)}([^<]*)</loc>", sitemap_path.read_text()) if sitemap_path.exists() else []
    sitemap = {normalize(url) for url in urls}
    expected_sitemap = {route_for(page) for page in all_pages}

    inbound = {url: [] for url in sitemap}
    issues = []
    blogposting_checked = 0

    for page in all_pages:
        text = page.read_text(encoding="utf-8")
        if not re.search(r"<!doctype html>", text, re.IGNORECASE):
            issues.append(f"missing doctype: {page.relative_to(ROOT)}")
        if not re.search(r'<meta name="description" content="[^"]+">', text):
            issues.append(f"missing meta description: {page.relative_to(ROOT)}")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        expected_canonical_route = route_for(page)
        if not canonical:
            issues.append(f"missing canonical: {page.relative_to(ROOT)}")
        elif normalize(canonical.group(1).replace(SITE, "")) != expected_canonical_route:
            issues.append(f"canonical mismatch: {page.relative_to(ROOT)} ({canonical.group(1)})")

        for href in URL_RE.findall(text):
            if not local_target_exists(page, href):
                issues.append(f"missing local target: {page.relative_to(ROOT)} -> {href}")
            if href.startswith("/"):
                target = normalize(href)
                if target in inbound:
                    inbound[target].append(page.relative_to(ROOT).as_posix())

        for match in SCRIPT_RE.finditer(text):
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError as exc:
                issues.append(f"invalid JSON-LD: {page.relative_to(ROOT)} ({exc})")
                continue
            if is_article_page(page):
                graph = data.get("@graph", [])
                blogposting = next((n for n in graph if n.get("@type") == "BlogPosting"), None)
                if blogposting is None:
                    issues.append(f"BlogPosting node missing from JSON-LD: {page.relative_to(ROOT)}")
                else:
                    blogposting_checked += 1
                    for key in REQUIRED_BLOGPOSTING_KEYS:
                        if key not in blogposting:
                            issues.append(f"BlogPosting missing {key}: {page.relative_to(ROOT)}")

    if sitemap != expected_sitemap:
        missing = sorted(expected_sitemap - sitemap)
        extra = sorted(sitemap - expected_sitemap)
        if missing:
            issues.append("pages missing from sitemap: " + ", ".join(missing))
        if extra:
            issues.append("sitemap routes without local page: " + ", ".join(extra))

    print(f"pages_checked={len(all_pages)}")
    print(f"sitemap_urls={len(sitemap)}")
    print(f"blogposting_records_checked={blogposting_checked}")
    print(f"urls_with_at_least_one_inbound_link={sum(len(set(v)) >= 1 for v in inbound.values())}")

    if issues:
        print("\n".join(issues), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
