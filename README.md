# LegalAIWorld — static migration (pilot)

Migrating legalaiworld.com off WordPress to a static HTML/CSS/JS site on
GitHub Pages, matching the pattern used by pickleballcosmos and
pickleballgyan.

**Status: pilot.** 3 of 24 articles migrated, plus the 5 static legal/about
pages. Not yet cut over — WordPress on Hostinger remains the live site.

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

## Not yet migrated / open questions
- Images currently still point at `legalaiworld.com/wp-content/uploads/...`
  — fine while WordPress stays live during the pilot, but before final
  cutover these need to be downloaded and self-hosted so the static site
  doesn't depend on the old WP install staying up.
- Category pages (`/category/ai-tools/` etc.) not yet built.
- On-site search (present in WP nav) not yet replicated.
- Remaining 21 articles not yet migrated.

Custom domain: legalaiworld.com (not yet pointed here — still on Hostinger/WordPress).
