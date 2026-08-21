# LegalAIWorld — Claude Code project instructions

Static site for legalaiworld.com, migrated off WordPress, matching the
pattern used by two sibling projects: pickleballcosmos and
pickleballgyan.

## Read this first

**The owner's #1 goal for this project is revenue, not traffic and not
technical polish.** The technical SEO here is done and done well — and
it is not the bottleneck. Before proposing or starting work, read
`CONTEXT.md` (gitignored, same directory) for the GSC data, the
monetization strategy, and the ranked priority list. Most
obvious-looking SEO tasks have been deliberately deprioritized there
for reasons backed by the search data. If `CONTEXT.md` is missing, ask
the user for it rather than guessing at business context from the code.

## What this repo is

- Static HTML/CSS/JS on GitHub Pages, custom domain `legalaiworld.com`.
  **Cutover from WordPress/Hostinger completed 2026-08-20** — DNS points
  at GitHub Pages and this repo is the live site.
- 27 articles + 5 legal/about pages + 4 category archive pages +
  homepage. Two former articles are now redirect stubs (consolidated
  after a cannibalization cleanup).
- **This repo is now the source of truth for content.** The old
  WordPress install is dormant; do not make content changes there. The
  workflow is git-only.

## Critical constraint: don't reset search rankings

Several articles rank on page 1-2 for real search terms — this took
roughly a year of accumulated domain trust to earn and is slow and
expensive to rebuild. **Every URL must keep its existing slug.** Google
treats a URL, not a "site," as the thing with ranking history — a
changed slug is a new page with zero history, even if the content is
identical.

Before changing any URL path, check whether it's already indexed
(Search Console → Pages → indexed). If yes, treat the slug as immutable
without a deliberate redirect plan. Use `scripts/make_redirect.py` when
a page genuinely must be retired.

## Content strategy (derived from GSC data, not opinion)

The search data is unambiguous about what earns clicks here:

- **Narrow, practical, specific articles win.** The best CTR on the site
  (5.48%) is a short "5 settings to change" piece; head-to-head
  comparisons are second (3.15%).
- **Broad "best X tools" roundups lose.** The worst performer has the
  *most* impressions on the site and a 0.05% CTR. **Do not write new
  broad roundups** — five already exist, they collectively earn very
  few clicks, and each new one cannibalizes the others.
- **Don't target head terms** ("legal ai chatbot", "ai contract review
  software"). The site ranks page 5-7 for all of them against Thomson
  Reuters, LexisNexis and Clio. Long-tail and differentiation only.
- **Thin content is a liability.** Anything under ~1,500 words is not
  competitive in this niche in 2026. Depth, original testing, real
  pricing tables.
- **E-E-A-T is the structural cap.** Legal is a YMYL niche and the site
  currently has no named, credentialed author. Any content work should
  move toward fixing that, not around it.

## Direction: interactive tools (planned, none built yet)

The project is moving beyond articles into interactive tools — a state
bar AI compliance checker, a "stack builder" recommender, a structured
legal AI tool index, downloadable policy/template packs. The rationale
and full ranked list live in `CONTEXT.md`; ask the user which one is
being built before starting.

Constraints that matter when building them:

- **Keep them static-compatible.** Quizzes, calculators and filterable
  databases should be client-side JS over a JSON data file — that works
  on GitHub Pages today and keeps the deploy story simple. Only email
  capture and PDF generation need anything server-side.
- **Migrating to Cloudflare Pages is under consideration** (free
  serverless functions, and it would also resolve the HTTPS cert
  issue). Don't assume it's happened — verify.
- **Tool data belongs in a JSON file**, not hardcoded in HTML, so it
  can be reused across the index, the recommender and comparison pages.
- **New tool pages still go through the standard workflow** —
  `build_index_pages.py`, `generate_sitemap.py`, then `audit_site.py`
  must exit 0. The audit expects a doctype, meta description and
  matching canonical on every page, so tool pages need those too.
- **Integrity guardrail:** if vendor placement is ever paid, it must be
  disclosed, and rankings must stay editorial with only the CTA/lead
  routing paid. Never quietly sell a ranking position — the tool's
  entire value is that a lawyer trusts it.

## Tooling

- `scripts/new_article.py` — the current path for **new** content.
  Source lives in `scripts/content/<slug>.html`.
- `scripts/migrate_article.py <slug> [--affiliate]` — legacy WordPress
  importer. Pulled a live WP article via the REST API plus the rendered
  `<head>`/`.entry-header`, extracted meta description, canonical, OG
  tags, Article JSON-LD and the real featured image (read from
  `.entry-header .post-thumb-img-content img`, **not** the `og:image`
  meta tag — WordPress's og:image was unreliable, see git history),
  downloaded and compressed the image into `assets/images/`. Now that
  WordPress is dormant this is mostly historical, but keep it for
  reference. `--affiliate` inserts the affiliate disclosure note.
- `scripts/migrate_page.py <slug>` — same for static pages, no images.
- `scripts/compress_images.py` — image compression (also baked into the
  migration pipeline).
- `scripts/make_redirect.py` — turns a retired URL into a redirect stub.
- `scripts/build_index_pages.py` — regenerates the homepage and the 4
  category archives from whatever's migrated. The category→article
  mapping is hardcoded near the top — update it when articles are added
  or recategorized. **Always re-run after adding/changing an article.**
- `scripts/generate_sitemap.py` — regenerates `sitemap.xml` from every
  `index.html` on disk. Run before the audit if pages changed.
- `scripts/audit_site.py` — integrity checks: doctype, meta description,
  matching canonical, every internal link/asset resolves, sitemap
  matches disk, and every article's JSON-LD has a `BlogPosting` node
  with `author`/`image`/`publisher`/`articleSection` (this repo's JSON-LD
  is WordPress/AIOSEO's `@graph` format, not a flat `Article` schema —
  see the adapted logic in the script if porting elsewhere). Runs in CI
  on every push/PR via `.github/workflows/site-audit.yml`.

**Standard workflow for any content change:**
```
python3 scripts/new_article.py <slug>        # or migrate_article.py
python3 scripts/build_index_pages.py
python3 scripts/generate_sitemap.py
python3 scripts/audit_site.py   # must exit 0 before committing
```

## Known project quirks

- Monetization wiring does not exist yet: **every outbound vendor link
  is untracked.** There's an Affiliate Disclosure page and no affiliate
  links. The Clio Duo review carries a placeholder URL and a
  `TODO(owner)` comment awaiting the owner's personal referral link.
- One article previously had a malformed WordPress slug (a literal
  `%e2%80%91` from an old WP bug). Fixed at the source and re-migrated
  — if you see references to a "hedge" or `EXCLUDE_ROUTES` in the
  scripts, that's leftover infrastructure from before the fix, unused
  but kept in case a similar issue recurs. Still wants a GSC
  re-indexing request (low priority).
- Images are AI-generated. Compressed 2026-08-21 (35MB → 2.4MB) and
  compression is now part of the pipeline.
- On-site search (present in the old WP nav) was deliberately not
  replicated.
- Tag archive pages (10 of them, low-value single-post tags) are
  intentionally not rebuilt.
- Don't commit `.DS_Store` or GSC export zips/folders.

## Sensitive/business context

Account details, GSC performance data, revenue strategy and the ranked
next-steps live in `CONTEXT.md` in this same directory — **not
committed to this public repo** (it's gitignored). Keep it that way:
traffic numbers, vendor prospect lists and revenue figures do not
belong in this file.
