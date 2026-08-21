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
            "westlaw-precision-ai-vs-lexis-ai-september-2025-best-ai-legal-research-assistant-for-u-s-lawyers",
            "doctrine-vs-predictice-vs-lucie-the-best-french-legal-ai-tools-in-2025",
            "in-house-counsel-stack-2025-lightweight-ai-toolkit-under-200-month",
            "best-ai-contract-review-software-2025",
            "hebbias-matrix-the-ai-search-tool-legal-teams-dont-know-they-need-2025",
            "cocounsel-deep-research-vs-lexis-protege-2025-which-agentic-legal-ai-wins",
            "meet-the-law-firm-2-0-startups-disrupting-legal-services-in-2025",
            "legal-tech-startups-to-watch-in-2025-the-ai-tools-raising-millions",
            "10-best-ai-tools-for-legal-research-in-2025",
            "clio-duo-review-2026-features-pricing-is-it-worth-it",
            "best-ai-billing-time-tracking-tools-for-law-firms-2026",
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
            "law-firm-ai-policy-template-2025-a-2-page-model-you-can-copy",
            "state-bar-ai-ethics-opinions-guide-for-lawyers",
            "the-eu-ai-act-the-august-2026-deadline-every-lawyer-needs-to-know-about",
        ],
    },
    "uncategorized": {
        "label": "Uncategorized",
        "slugs": [
            "5-chatgpt-settings-to-change-immediately-if-youre-a-lawyer",
        ],
    },
}


BLURBS = {
    "ai-tools": "Reviews and comparisons of the AI tools built for legal work \u2014 what they cost, what they actually do, and where they fall short.",
    "legal-research": "AI-assisted legal research: platform comparisons, accuracy and hallucination findings, and how lawyers are using these tools day to day.",
    "compliance": "The rules governing AI use in practice \u2014 bar ethics opinions, court orders, the EU AI Act, and what firms need in a written policy.",
    "uncategorized": "Everything else worth reading.",
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
    img_match = re.search(r'<img class="featured-image" src="([^"]*)"', html)
    image = img_match.group(1) if img_match else ""
    return {"slug": slug, "title": title, "category": category, "date": date,
            "desc": desc, "image": image}


def plate_label(category: str) -> str:
    """Label for the plate shown on articles with no hero image."""
    return category.strip() or "LegalAIWorld"


def trim(text: str, limit: int = 165) -> str:
    """Shorten a meta description to a card dek without cutting mid-word."""
    text = text.replace(" -- ", " &mdash; ")
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:.\u2014-")
    return cut + "&hellip;"


def card(article: dict, lead: bool = False) -> str:
    href = "/" + article["slug"] + "/"
    cls = "card card--lead" if lead else "card"

    if article["image"]:
        # The lead image is above the fold, so it must not be lazy-loaded.
        loading = "eager" if lead else "lazy"
        thumb = (
            f'<span class="card-thumb">'
            f'<img src="{article["image"]}" alt="" loading="{loading}" decoding="async">'
            f'</span>'
        )
    else:
        thumb = (
            f'<span class="card-thumb card-thumb--placeholder">'
            f'<img src="/assets/logo.svg" alt="" aria-hidden="true">'
            f'<span aria-hidden="true">{plate_label(article["category"])}</span>'
            f'</span>'
        )

    return (
        f'<a class="{cls}" href="{href}">'
        f'{thumb}'
        f'<span class="card-body">'
        f'<span class="eyebrow">{article["category"]}</span>'
        f'<h3>{article["title"]}</h3>'
        f'<p class="dek">{trim(article["desc"])}</p>'
        f'<span class="foot">{article["date"]} &middot; Read article &rarr;</span>'
        f'</span>'
        f'</a>'
    )


def cards_html(articles: list, lead: bool = False) -> str:
    """Render a grid, optionally promoting the newest article to a lead."""
    if not articles:
        return ""
    if lead:
        return "\n".join([card(articles[0], lead=True)] + [card(a) for a in articles[1:]])
    return "\n".join(card(a) for a in articles)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - LegalAIWorld</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://legalaiworld.com/category/{slug}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&amp;display=swap">
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
<p class="meta">{blurb}</p>
</section>
<hr class="hero-rule">
<div class="section-head"><h2>{count} articles</h2></div>
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&amp;display=swap">
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
<div class="eyebrow">Independent legal technology coverage</div>
<h1>Your guide to AI in law</h1>
<p class="meta">Practical, no-hype analysis of the tools lawyers actually use &mdash; legal AI chatbots, contract review software, research platforms and the compliance rules that govern them. Real pricing, verified against primary sources.</p>
<div class="hero-actions">
<a class="pill" href="/category/ai-tools/">AI Tools</a>
<a class="pill" href="/category/legal-research/">Legal Research</a>
<a class="pill" href="/category/compliance/">Compliance</a>
<a class="pill" href="/about-us/">About</a>
</div>
</section>
<hr class="hero-rule">

<div class="section-head"><h2>Latest</h2></div>
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
            blurb=BLURBS.get(cat_slug, ""),
            count=len(articles),
            cards=cards_html(articles, lead=True),
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
    home = HOME_TEMPLATE.format(latest_cards=cards_html(deduped, lead=True))
    (ROOT / "index.html").write_text(home, encoding="utf-8")
    print(f"Wrote index.html ({len(all_articles)} articles)")


if __name__ == "__main__":
    main()
