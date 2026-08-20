# LegalAIWorld — static migration

Migrating legalaiworld.com off WordPress to a static HTML/CSS/JS site on
GitHub Pages, matching the pattern used by pickleballcosmos and
pickleballgyan.

**Status: full content migrated, not yet cut over.** All 24 articles,
4 category pages, the homepage, and the 5 static legal/about pages are
built, with all 24 featured images downloaded and self-hosted under
`assets/images/`. WordPress on Hostinger remains the live site until
Phase 3 verification (on-site search, broken-link audit) is done.

## Why
- Real search-engine equity already exists (page-1 rankings for several
  articles) — every migrated URL must exactly match its WordPress slug so
  Google treats it as the same page, not a new one.
- Simpler ops: no PHP/plugin vulnerability surface, git history, free
  GitHub Pages hosting on the existing custom domain.

## Migration tooling
- `scripts/migrate_article.py <slug> [--affiliate]` — pulls a live WP
  article via the REST API + live page `<head>`, extracts the exact meta
  description, canonical, OG tags, and Article JSON-LD, downloads the
  real featured image (read from `.entry-header`, not the `og:image` tag
  — see note below) into `assets/images/`, and writes a static page at
  the same URL path.
- `scripts/migrate_page.py <slug>` — same idea for static pages (About,
  Disclaimer, etc), no images.
- `scripts/build_index_pages.py` — regenerates the homepage and the 4
  category archive pages from whatever's already migrated. Re-run this
  any time an article is re-migrated.

## Known issue: og:image is not a reliable image source
WordPress's own `<meta property="og:image">` tag on this site frequently
falls back to the generic site logo even when a real featured image is
set on the post — apparently an AIOSEO quirk (a per-post "social image"
field that was never set, separate from the featured image). The actual
displayed image lives in `.entry-header .post-thumb-img-content img`.
`migrate_article.py` reads from there, not from `og:image`, and writes
the correct URL back into all three places (the visible image, the
`og:image` tag, and the JSON-LD) — this is a fidelity *improvement* over
the current live site's social-share previews, not a deviation from it,
and has no bearing on Google Web-search rankings either way.

## Known issue: one malformed slug, served two ways as a hedge
`law-firm-ai-policy-template-2025-a-2%e2%80%91page-model-you-can-copy/` has a
pre-existing WordPress bug: its slug (and the canonical URL WordPress itself
declares) contains the literal characters `%e2%80%91` rather than an actual
Unicode non-breaking hyphen. Google has indexed that exact literal string
(it's what WP's own `<link rel="canonical">` declares), so the canonical
tag, JSON-LD, and every internal link here keep using it as-is.

But the audit script caught a real problem with that: a standard web
server decodes `%XX` sequences in the request path before looking up a
file, so a browser/crawler requesting that URL will actually look for a
directory containing the literal Unicode hyphen (`‑`), not the literal
percent-encoded string. Both directories exist here with identical
content as a hedge — `law-firm-ai-policy-template-2025-a-2‑page-model-you-can-copy/`
is a compatibility duplicate, excluded from the sitemap and from
`audit_site.py`'s page count (see `EXCLUDE_ROUTES` in both scripts) so
it isn't treated as a second real page.

**Verified live against GitHub Pages (2026-08-20):** temporarily removed
`CNAME`, pushed, and curled the raw `aaditya7-codes.github.io/legalaiworld/`
URL directly. Both the percent-encoded and the decoded-Unicode variant
resolve with HTTP 200 and the correct article title — so the hedge
works and either form of the URL will serve real content once cut over.
Also spot-checked the homepage, a normal article, a category page, a
self-hosted image, and `sitemap.xml` — all 200. `CNAME` restored
immediately after.

## CI
`.github/workflows/site-audit.yml` runs `scripts/audit_site.py` on every
push/PR to `main` — checks every page has a doctype, meta description,
and matching canonical; every internal link and asset resolves; the
sitemap matches what's actually on disk; and every article's JSON-LD has
a `BlogPosting` node with `author`/`image`/`publisher`/`articleSection`.
Run `python scripts/generate_sitemap.py` before it if pages were added
or removed, since the audit checks sitemap-vs-disk consistency.

## Not yet done / open questions
- On-site search (present in WP nav) not yet replicated.
- Homepage/category cards don't show image thumbnails yet — text-only
  cards. Optional polish, not a correctness issue.
- Images total ~42MB across 24 files (AI-generated, high-res) — fine for
  GitHub Pages, but worth compressing before cutover for page-speed.
- Tag archive pages (10 of them) intentionally not rebuilt — low-value,
  single-post tag pages not worth recreating.

Custom domain: legalaiworld.com (not yet pointed here — still on Hostinger/WordPress).
