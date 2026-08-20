# LegalAIWorld — static migration

Migrating legalaiworld.com off WordPress to a static HTML/CSS/JS site on
GitHub Pages, matching the pattern used by pickleballcosmos and
pickleballgyan.

**Status: full content migrated, not yet cut over.** All 24 articles,
4 category pages, the homepage, and the 5 static legal/about pages are
built. WordPress on Hostinger remains the live site until Phase 3
verification (image hosting, search, broken-link check) is done.

## Why
- Real search-engine equity already exists (page-1 rankings for several
  articles) — every migrated URL must exactly match its WordPress slug so
  Google treats it as the same page, not a new one.
- Simpler ops: no PHP/plugin vulnerability surface, git history, free
  GitHub Pages hosting on the existing custom domain.

## Migration tooling
- `scripts/migrate_article.py <slug> [--affiliate]` — pulls a live WP
  article via the REST API + live page `<head>`, extracts the exact meta
  description, canonical, OG tags, and Article JSON-LD, and writes a
  static page at the same URL path.
- `scripts/migrate_page.py <slug>` — same idea for static pages (About,
  Disclaimer, etc).

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
- Images currently still point at `legalaiworld.com/wp-content/uploads/...`
  — fine while WordPress stays live, but before final cutover these need
  to be downloaded and self-hosted so the static site doesn't depend on
  the old WP install staying up.
- On-site search (present in WP nav) not yet replicated.
- Tag archive pages (10 of them) intentionally not rebuilt — low-value,
  single-post tag pages not worth recreating.
- No automated link/sitemap audit yet (Cosmos has `audit_site.py` for
  this — worth porting over before cutover).

Custom domain: legalaiworld.com (not yet pointed here — still on Hostinger/WordPress).
