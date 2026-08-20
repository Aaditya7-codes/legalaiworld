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

## Known issue: one malformed slug
`law-firm-ai-policy-template-2025-a-2%e2%80%91page-model-you-can-copy/` has a
pre-existing WordPress bug: its slug (and the canonical URL WordPress itself
declares) contains the literal characters `%e2%80%91` rather than an actual
Unicode non-breaking hyphen. This is not something introduced by the
migration — WordPress's own REST API and `<link rel="canonical">` both
serve this exact malformed string, so it's what Google has indexed. The
directory here matches it exactly. Confirm this resolves correctly once
served by GitHub Pages before cutover (a local `python -m http.server`
test 404s on it because it decodes the request path differently than
whatever server stack is behind GitHub Pages / the original WordPress
site — needs a live check, not just a local one).

## Not yet done / open questions
- On-site search (present in WP nav) not yet replicated.
- Homepage/category cards don't show image thumbnails yet — text-only
  cards. Optional polish, not a correctness issue.
- Images total ~42MB across 24 files (AI-generated, high-res) — fine for
  GitHub Pages, but worth compressing before cutover for page-speed.
- Tag archive pages (10 of them) intentionally not rebuilt — low-value,
  single-post tag pages not worth recreating.
- No automated link/sitemap audit yet (Cosmos has `audit_site.py` for
  this — worth porting over before cutover).

Custom domain: legalaiworld.com (not yet pointed here — still on Hostinger/WordPress).
