# LegalAIWorld — Claude Code project instructions

Static migration of legalaiworld.com off WordPress, matching the pattern
used by two sibling projects: pickleballcosmos and pickleballgyan.

## What this repo is

- Static HTML/CSS/JS, deployed on GitHub Pages, custom domain
  `legalaiworld.com` (not yet cut over — WordPress on Hostinger is still
  the live site; `CNAME` in this repo is inert until DNS changes).
- 24 articles + 5 legal/about pages + 4 category archive pages + homepage.
- The source of truth for content is the live WordPress site
  (`legalaiworld.com`, WP Admin), not this repo. This repo is a
  generated mirror — re-run the migration scripts after any WordPress
  content change, don't hand-edit generated HTML unless you're also
  making the same change in WordPress.

## Critical constraint: don't reset search rankings

Several articles already rank on page 1 for real search terms — this
took roughly a year of accumulated domain trust to earn and is slow/
expensive to rebuild. **Every migrated URL must exactly match its
WordPress slug.** Google treats a URL, not a "site," as the thing with
ranking history — a changed slug is a new page with zero history to
Google, even if the content is identical.

Before changing any URL path in this repo, check whether the
corresponding WordPress URL is already indexed (Search Console → Pages
→ indexed) — if yes, treat the slug as immutable without a deliberate
redirect plan.

## Migration tooling

- `scripts/migrate_article.py <slug> [--affiliate]` — pulls one live WP
  article via the REST API + the live page's rendered `<head>`/
  `.entry-header`, extracts meta description, canonical, OG tags,
  Article JSON-LD, and the real featured image (reads
  `.entry-header .post-thumb-img-content img`, **not** the `og:image`
  meta tag — WordPress's own og:image is unreliable, see git history
  for why), downloads the image into `assets/images/`, and writes a
  static page at the matching URL path. Pass `--affiliate` for listicle/
  roundup articles that need the affiliate disclosure note inserted.
- `scripts/migrate_page.py <slug>` — same idea for static pages (About,
  Disclaimer, Terms, Privacy), no images.
- `scripts/build_index_pages.py` — regenerates the homepage and the 4
  category archive pages from whatever's currently migrated. The
  category→article mapping is hardcoded near the top of this file —
  update it when articles are added/recategorized. **Always re-run this
  after migrating a new/changed article.**
- `scripts/generate_sitemap.py` — regenerates `sitemap.xml` from every
  `index.html` actually on disk. Run before the audit if pages were
  added or removed.
- `scripts/audit_site.py` — integrity checks: every page has a doctype,
  meta description, and matching canonical; every internal link/asset
  resolves; sitemap matches disk; every article's JSON-LD has a
  `BlogPosting` node with `author`/`image`/`publisher`/`articleSection`
  (this repo's JSON-LD is WordPress/AIOSEO's `@graph` format, not a flat
  `Article` schema — see the adapted logic in this script if porting to
  another project). Runs in CI on every push/PR via
  `.github/workflows/site-audit.yml`.

**Standard workflow for any content change:**
```
python3 scripts/migrate_article.py <slug> [--affiliate]
python3 scripts/build_index_pages.py
python3 scripts/generate_sitemap.py
python3 scripts/audit_site.py   # must exit 0 before committing
```

## Known project quirks

- One article previously had a malformed WordPress slug (a literal
  `%e2%80%91` baked into the URL from an old WP bug). Fixed at the
  source in WordPress and re-migrated — if you see references to a
  "hedge" or `EXCLUDE_ROUTES` in the scripts, that's leftover
  infrastructure from before the fix, currently unused but kept in case
  a similar issue recurs.
- Images are AI-generated, high-res (~1-4MB each, ~42MB total across 24
  files) — not yet compressed. Fine for GitHub Pages, worth addressing
  before final cutover for page speed.
- On-site search (present in the live WP nav) has not been replicated.
- Tag archive pages (10 of them, low-value single-post tags) are
  intentionally not rebuilt.

## Sensitive/business context

Account details, revenue research, and strategic next-steps live in
`CONTEXT.md` in this same directory — **not committed to this public
repo** (it's gitignored). If you're picking up this project fresh and
that file is missing, ask the user for it rather than guessing at
business context from the code alone.
