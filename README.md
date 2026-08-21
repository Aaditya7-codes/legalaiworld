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

## Resolved: the malformed slug is fixed at the source
`law-firm-ai-policy-template-2025-a-2%e2%80%91page-model-you-can-copy/` used
to have a pre-existing WordPress bug: its slug (and the canonical URL
WordPress itself declared) contained the literal characters `%e2%80%91`
rather than an actual Unicode non-breaking hyphen.

Before fixing it at the source, this was verified live against GitHub
Pages (2026-08-20): temporarily removed `CNAME`, pushed, and curled the
raw `aaditya7-codes.github.io/legalaiworld/` URL directly — both the
percent-encoded and the decoded-Unicode variant resolved with HTTP 200
and the correct article title, alongside the homepage, a normal article,
a category page, a self-hosted image, and `sitemap.xml`, also all 200.
`CNAME` restored immediately after.

Since the article had **zero indexing/ranking to protect** (it was one
of the "crawled — currently not indexed" pages), the safer permanent fix
was to correct the slug directly in WordPress rather than carry the
hedge forward indefinitely. Fixed via the block editor's Permalink field
to the clean `law-firm-ai-policy-template-2025-a-2-page-model-you-can-copy`
— verified live via the REST API: the new URL returns 200 and its own
`<link rel="canonical">` now matches. The static repo has been
re-migrated to match, and the old percent-encoded/decoded-Unicode hedge
directories have been removed. Next: request re-indexing on the new URL
via GSC's URL Inspection tool.

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
