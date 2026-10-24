#!/usr/bin/env python3
"""Set existing page last-modified metadata and labelled update dates for Ahaneiffel."""
from pathlib import Path
import re
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
ISO_DATE = "2026-10-24"
PERSIAN_DATE = "۱۴۰۵/۰۸/۰۲"
ASCII_PERSIAN_DATE = "1405/08/02"

changed = []
for path in ROOT.rglob("*.html"):
    if any(part in {".git", ".github"} for part in path.parts):
        continue
    original = path.read_text(encoding="utf-8")
    updated = original

    # Update structured last-modified metadata only where it already exists.
    updated = re.sub(
        r'("dateModified"\s*:\s*")[^"]+(")',
        lambda m: m.group(1) + ISO_DATE + m.group(2),
        updated,
    )
    updated = re.sub(
        r'(<meta\s+[^>]*(?:property|name)=["\'](?:article:modified_time|last-modified|dateModified)["\'][^>]*content=["\'])[^"\']+',
        lambda m: m.group(1) + ISO_DATE,
        updated,
        flags=re.I,
    )

    # Update Persian/ISO dates only when they are explicitly attached to an update label.
    label_pattern = r'((?:آخرین\s*(?:به‌روزرسانی|بروزرسانی|تغییر)|(?:به‌روزرسانی|بروزرسانی)\s*(?:صفحه|محتوا|تاریخ)?|Updated\s*:?)\s*(?:[:：\-–]|</[^>]+>\s*)?\s*)(?:۱۴۰۵|1405|2026)[/\-年][۰-۹0-۹\d]{1,2}[/\-月][۰-۹0-۹\d]{1,2}'
    updated = re.sub(label_pattern, lambda m: m.group(1) + PERSIAN_DATE, updated, flags=re.I)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

# Keep sitemap lastmod dates aligned with the HTML pages.
for path in ROOT.rglob("*.xml"):
    if any(part in {".git", ".github"} for part in path.parts):
        continue
    original = path.read_text(encoding="utf-8")
    updated = re.sub(r"(<lastmod>)[^<]+(</lastmod>)", lambda m: m.group(1) + ISO_DATE + m.group(2), original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

print(f"Updated {len(changed)} HTML/XML files for dateModified / labelled update-date / sitemap lastmod metadata.")
for item in changed:
    print(item)
