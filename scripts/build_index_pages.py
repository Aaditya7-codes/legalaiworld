#!/usr/bin/env python3
"""Build the homepage and category archive pages from the migrated articles.

Reads title/date/description straight out of each generated article's own
<head>, so it stays in sync with whatever migrate_article.py last wrote.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = {
    "ai-tools": {
        "label": "AI Tools",
        "slugs": [
            "westlaw-ai-and-lexis-ai-still-hallucinate-what-the-stanford-study-actually-found",
            "chatgpt-vs-claude-the-ai-showdown-every-legal-professional-needs-to-watch",
            "best-legal-ai-chatbots-2026-the-12-that-actually-help-lawyers-and-what-each-is-best-at",
            "7-best-legal-ai-chatbots-for-lawyers-in-september-2025-reviewed",
            "westlaw-precision-ai-vs-lexis-ai-september-2025-best-ai-legal-research-assistant-for-u-s-lawyers",
            "doctrine-vs-predictice-vs-lucie-the-best-french-legal-ai-tools-in-2025",
            "in-house-counsel-stack-2025-lightweight-ai-toolkit-under-200-month",
            "best-ai-contract-review-software-2025",
            "hebbias-matrix-the-ai-search-tool-legal-teams-dont-know-they-need-2025",
            "cocounsel-deep-research-vs-lexis-protege-2025-which-agentic-legal-ai-wins",
            "meet-the-law-firm-2-0-startups-disrupting-legal-services-in-2025",
            "legal-tech-startups-to-watch-in-2025-the-ai-tools-raising-millions",
            "10-best-ai-tools-for-legal-research-in-2025",
            "7-best-ai-tools-for-contract-review-lawyers-in-2025",
        ],
    },
    "legal-research": {
        "label": "Legal Research",
        "slugs": [
            "ai-hallucinations-in-court-every-lawyer-needs-to-read-this-before-their-next-filing",
            "10-genai-prompts-every-contract-lawyer-should-use-drafting-redlines-negotiation",
            "top-legal-ai-features-lawyers-actually-use-every-week-2025-survey",
            "big-laws-ai-overhaul-inside-the-firms-that-are-winning-the-innovation-race",
            "why-85-of-lawyers-use-ai-weekly-in-2025-and-your-firm-should-too",
            "10-best-ai-tools-for-legal-research-in-2025",
        ],
    },
    "compliance": {
        "label": "Compliance",
        "slugs": [
            "using-chatgpt-or-claude-on-a-client-matter-a-federal-judge-just-issued-a-warning-every-lawyer-needs-to-hear",
            "what-is-agentic-ai-and-why-every-lawyer-needs-to-understand-it-before-2027",
            "law-firm-ai-policy-template-2025-a-2%e2%80%91page-model-you-can-copy",
        ],
    },
    "uncategorized": {
        "label": "Uncategorized",
        "slugs": [
            "the-eu-ai-act-the-august-2026-deadline-every-lawyer-needs-to-know-about",
            "5-chatgpt-settings-to-change-immediately-if-youre-a-lawyer",
        ],
    },
}


def read_meta(slug: str) -> dict:
    path = ROOT / slug / "index.html"
    html = path.read_text(encoding="utf-8")
    title = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1).strip()
    date_match = re.search(r'class="meta"><span class="eyebrow">([^<]*)</span> &middot; ([\d-]+)', html)
    category = date_match.group(1) if date_match else ""
    date = date_match.group(2) if date_match else ""
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = desc_match.group(1) if desc_match else ""
    return {"slug": slug, "title": title, "category": category, "date": date, "desc": desc}


def card(article: dict) -> str:
    href = "/" + article["slug"] + "/"
    return (
        f'<a class="card" href="{href}">'
        f'<span class="eyebrow">{article["category"]}</span>'
        f'<h3>{article["title"]}</h3>'
        f'<div class="foot">{article["date"]} &middot; Read article &rarr;</div>'
        f'</a>'
    )


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - LegalAIWorld</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://legalaiworld.com/category/{slug}/">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<header class="masthead">
<div class="container">
<a class="brand" href="/"><img src="/assets/logo.svg" alt=""><span>LegalAIWorld</span></a>
<nav class="main-nav"></nav>
</div>
</header>

<main>
<div class="container">
<section class="hero">
<div class="eyebrow">Category</div>
<h1>{label}</h1>
</section>
<div class="card-grid">
{cards}
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

HOME_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LegalAIWorld - Your Guide to AI in Law</title>
<meta name="description" content="Practical, no-hype coverage of AI tools for lawyers: legal AI chatbots, contract review software, compliance guidance, and legal research tools.">
<link rel="canonical" href="https://legalaiworld.com/">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<header class="masthead">
<div class="container">
<a class="brand" href="/"><img src="/assets/logo.svg" alt=""><span>LegalAIWorld</span></a>
<nav class="main-nav"></nav>
</div>
</header>

<main>
<div class="container">
<section class="hero">
<div class="eyebrow">LegalAIWorld</div>
<h1>Your Guide to AI in Law</h1>
<p class="meta">Practical, no-hype coverage of AI tools for lawyers &mdash; legal AI chatbots, contract review software, compliance guidance, and legal research.</p>
</section>

<div class="section-head"><h2>Latest Articles</h2></div>
<div class="card-grid">
{latest_cards}
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


def main() -> None:
    all_articles = []
    for cat_slug, cat in CATEGORIES.items():
        articles = [read_meta(s) for s in cat["slugs"]]
        articles.sort(key=lambda a: a["date"], reverse=True)
        all_articles.extend(articles)

        out_dir = ROOT / "category" / cat_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        page = PAGE_TEMPLATE.format(
            title=cat["label"],
            description=f"{cat['label']} articles from LegalAIWorld.",
            slug=cat_slug,
            label=cat["label"],
            cards="\n".join(card(a) for a in articles),
        )
        (out_dir / "index.html").write_text(page, encoding="utf-8")
        print(f"Wrote category/{cat_slug}/index.html ({len(articles)} articles)")

    seen = set()
    deduped = []
    for a in all_articles:
        if a["slug"] not in seen:
            seen.add(a["slug"])
            deduped.append(a)
    deduped.sort(key=lambda a: a["date"], reverse=True)
    home = HOME_TEMPLATE.format(latest_cards="\n".join(card(a) for a in deduped))
    (ROOT / "index.html").write_text(home, encoding="utf-8")
    print(f"Wrote index.html ({len(all_articles)} articles)")


if __name__ == "__main__":
    main()
