#!/usr/bin/env python3
"""Check canonical and JSON-LD markup in indexable HTML files.

Run from repository root: python scripts/seo_structured_data_integrity.py
Uses HTMLParser instead of fragile regular expressions for HTML attributes.
"""
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ERRORS: list[str] = []
WARNINGS: list[str] = []
CHECKED = 0
SKIPPED = 0
ROOT = Path(".")
ALLOWED_HOSTS = {"ahaneiffel.top", "www.ahaneiffel.top"}


class SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.is_html = False
        self.noindex = False
        self.canonicals: list[str] = []
        self.jsonld_blocks: list[str] = []
        self._in_jsonld = False
        self._script_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "html":
            self.is_html = True
        if tag == "meta" and values.get("name", "").strip().lower() == "robots":
            if "noindex" in values.get("content", "").lower():
                self.noindex = True
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            href = values.get("href", "").strip()
            if href:
                self.canonicals.append(href)
        if tag == "script" and values.get("type", "").strip().lower() == "application/ld+json":
            self._in_jsonld = True
            self._script_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._script_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_jsonld:
            self.jsonld_blocks.append("".join(self._script_parts).strip())
            self._script_parts = []
            self._in_jsonld = False


for path in ROOT.rglob("*.html"):
    if ".git" in path.parts or "__pycache__" in path.parts:
        continue
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        ERRORS.append(f"{path}: unable to read HTML: {exc}")
        continue

    parser = SEOParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:
        ERRORS.append(f"{path}: HTML parser error: {exc}")
        continue

    if not parser.is_html:
        SKIPPED += 1
        continue
    if parser.noindex:
        SKIPPED += 1
        continue

    CHECKED += 1
    if not parser.canonicals:
        ERRORS.append(f"{path}: missing canonical")
    elif len(parser.canonicals) > 1:
        ERRORS.append(f"{path}: multiple canonical links ({len(parser.canonicals)})")

    for url in parser.canonicals:
        parsed = urlparse(url)
        if "index.html" in parsed.path.lower():
            ERRORS.append(f"{path}: canonical contains index.html: {url}")
        if parsed.scheme and parsed.netloc and parsed.netloc.lower() not in ALLOWED_HOSTS:
            ERRORS.append(f"{path}: unexpected canonical host: {url}")
        if parsed.scheme and parsed.scheme.lower() != "https":
            ERRORS.append(f"{path}: canonical is not HTTPS: {url}")

    for block in parser.jsonld_blocks:
        if not block:
            ERRORS.append(f"{path}: empty JSON-LD block")
            continue
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            ERRORS.append(f"{path}: invalid JSON-LD at line {exc.lineno}, column {exc.colno}")
        if "index.html" in block.lower():
            WARNINGS.append(f"{path}: JSON-LD contains index.html URL; compare it with the canonical before changing schema URLs")

print(f"SEO integrity audit: {CHECKED} indexable HTML documents checked; {SKIPPED} non-HTML/noindex documents skipped")
for warning in WARNINGS[:100]:
    print(f"WARN {warning}")
for error in ERRORS[:300]:
    print(f"ERROR {error}")
if CHECKED == 0:
    print("ERROR audit did not inspect any indexable HTML documents; refusing false-green result")
    sys.exit(1)
if ERRORS:
    print(f"FAIL: {len(ERRORS)} issue(s) found.")
    sys.exit(1)
print("PASS: canonical and JSON-LD integrity checks passed.")
