#!/usr/bin/env python3
"""One-time backfill: resize + convert the 24 already-migrated article
images from full-size PNG to compressed JPEG, and rewrite every HTML
reference (img src, og:image, JSON-LD image url/width/height) to match.

Run once from repo root: python3 scripts/compress_images.py

Safe to re-run: images already converted to .jpg are skipped, and HTML
rewrites are no-ops once the filenames/dimensions already match.

For future migrations, migrate_article.py's localize_image() now does
this compression at download time, so this script should not need to
run again except as a one-off cleanup.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "assets" / "images"
MAX_WIDTH = 1200
JPEG_QUALITY = 84


def compress_one(png_path: Path) -> tuple[str, str, int, int] | None:
    """Resize+convert one PNG to JPEG. Returns (old_name, new_name, w, h),
    or None if there's no PNG left to convert (already done)."""
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    if w > MAX_WIDTH:
        h = round(h * MAX_WIDTH / w)
        w = MAX_WIDTH
        im = im.resize((w, h), Image.LANCZOS)

    jpg_path = png_path.with_suffix(".jpg")
    im.save(jpg_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    png_path.unlink()
    return png_path.name, jpg_path.name, w, h


def rewrite_references(html_path: Path, old_name: str, new_name: str, w: int, h: int) -> bool:
    text = html_path.read_text(encoding="utf-8")
    if old_name not in text:
        return False

    updated = text.replace(old_name, new_name)

    # JSON-LD ImageObject blocks carry explicit width/height right after
    # the url for that specific image -- scope the number replacement to
    # text immediately following this filename so unrelated ImageObjects
    # (organization logo, author avatar) are untouched.
    escaped_name = re.escape(new_name)
    pattern = re.compile(
        rf'({escaped_name}"(?:,"@id":"[^"]*")?,"width":)\d+(,"height":)\d+'
    )
    updated = pattern.sub(rf"\g<1>{w}\g<2>{h}", updated)

    html_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    conversions = []
    for png_path in sorted(IMAGES_DIR.glob("*.png")):
        conversions.append(compress_one(png_path))

    if not conversions:
        print("No PNGs left in assets/images/ -- nothing to compress.")
    else:
        for old_name, new_name, w, h in conversions:
            print(f"compressed {old_name} -> {new_name} ({w}x{h})")

    if not conversions:
        return

    html_files = list(ROOT.glob("*/index.html"))
    for old_name, new_name, w, h in conversions:
        touched = [p for p in html_files if rewrite_references(p, old_name, new_name, w, h)]
        for p in touched:
            print(f"  updated {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
