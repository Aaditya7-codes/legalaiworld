#!/usr/bin/env python3
"""Generate sitemap.xml from every index.html in the repo."""
from __future__ import annotations

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://legalaiworld.com"
EXCLUDE_DIRS = {"assets", "scripts", ".git"}
# Was used to exclude a compatibility duplicate for a malformed WordPress
# slug; the slug's been fixed at the source (see README), so this is empty
# now but left in place in case a similar hedge is ever needed again.
EXCLUDE_ROUTES: set[str] = set()


def route_for(page: Path) -> str:
    rel = page.relative_to(ROOT)
    if rel.parent == Path("."):
        return "/"
    return f"/{rel.parent.as_posix()}/"


def main() -> None:
    routes = sorted(
        r for r in (
            route_for(p)
            for p in ROOT.rglob("index.html")
            if p.relative_to(ROOT).parts[0] not in EXCLUDE_DIRS
        )
        if r not in EXCLUDE_ROUTES
    )
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in routes:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}{route}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote sitemap.xml with {len(routes)} URLs")


if __name__ == "__main__":
    main()
