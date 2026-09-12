#!/usr/bin/env python3
"""Audit static HTML internal links, canonicals and orphan indexable pages.

Designed for the Ahaneiffel GitHub Pages repository. The script reads the
checked-out repository, resolves directory-style URLs to index.html, ignores
external/mail/tel/javascript/hash links, and reports broken internal targets,
www-host links, duplicate canonical URLs, and indexable orphan pages.
"""
from __future__ import annotations

import html
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
SITE_HOSTS = {"ahaneiffel.top", "www.ahaneiffel.top"}
SKIP_DIRS = {".git", ".github", "node_modules"}
HREF_RE = re.compile(r"<(?:a|link)\b[^>]*\bhref\s*=\s*([\"'])(.*?)\1", re.I | re.S)
CANON_RE = re.compile(
    r'<link\b[^>]*rel\s*=\s*["\'][^"\']*canonical[^"\']*["\'][^>]*href\s*=\s*["\']([^"\']+)',
    re.I | re.S,
)
META_ROBOTS_RE = re.compile(
    r'<meta\b[^>]*name\s*=\s*["\']robots["\'][^>]*content\s*=\s*["\']([^"\']+)',
    re.I | re.S,
)


def html_files():
    for p in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def public_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel


def resolve_target(raw: str, source: Path):
    raw = html.unescape(raw).strip()
    if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        if parsed.netloc and parsed.hostname not in SITE_HOSTS:
            return None
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return None
        target_url = unquote(parsed.path or "/")
    else:
        target_url = unquote(parsed.path)
        if target_url.startswith("/"):
            pass
        else:
            target_url = "/" + str((source.parent / target_url).resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    target_url = target_url.split("#", 1)[0] or "/"
    if not target_url.startswith("/"):
        target_url = "/" + target_url
    return target_url


def target_file(url_path: str):
    rel = url_path.lstrip("/")
    if not rel:
        return ROOT / "index.html"
    p = ROOT / rel
    if p.is_file():
        return p
    if p.suffix == "":
        idx = p / "index.html"
        if idx.is_file():
            return idx
    if p.suffix == ".html":
        return p if p.is_file() else None
    return None


def canonical_value(text: str):
    m = CANON_RE.search(text)
    return html.unescape(m.group(1)).strip() if m else None


def is_indexable(text: str):
    m = META_ROBOTS_RE.search(text)
    if not m:
        return True
    return "noindex" not in m.group(1).lower()


def main():
    pages = list(html_files())
    url_to_file = {public_url(p): p for p in pages}
    inbound = Counter()
    broken = []
    www_links = []
    duplicate_canonicals = defaultdict(list)
    orphan = []

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        canon = canonical_value(text)
        if canon:
            parsed = urlparse(canon)
            if parsed.hostname in SITE_HOSTS:
                cpath = parsed.path or "/"
                duplicate_canonicals[cpath].append(page)
                if parsed.hostname == "www.ahaneiffel.top":
                    www_links.append((public_url(page), canon))

        for _, raw in HREF_RE.findall(text):
            target = resolve_target(raw, page)
            if target is None:
                continue
            parsed = urlparse(raw)
            if parsed.hostname == "www.ahaneiffel.top":
                www_links.append((public_url(page), raw))
            target_page = target_file(target)
            if target_page is None:
                broken.append((public_url(page), raw, target))
            else:
                inbound[public_url(target_page)] += 1

    for page in pages:
        u = public_url(page)
        text = page.read_text(encoding="utf-8", errors="replace")
        if is_indexable(text) and inbound[u] == 0 and u != "/":
            orphan.append(u)

    print(f"HTML pages: {len(pages)}")
    print(f"Broken internal links: {len(broken)}")
    for src, raw, target in broken[:100]:
        print(f"BROKEN | {src} | {raw} | resolved={target}")
    print(f"www host references: {len(www_links)}")
    for src, raw in www_links[:100]:
        print(f"WWW | {src} | {raw}")
    dupes = {k: v for k, v in duplicate_canonicals.items() if len(v) > 1}
    print(f"Duplicate canonical targets: {len(dupes)}")
    for target, files in list(dupes.items())[:100]:
        print("CANONICAL-DUP | " + target + " | " + ", ".join(public_url(p) for p in files))
    print(f"Indexable orphan pages: {len(orphan)}")
    for u in orphan[:200]:
        print(f"ORPHAN | {u}")

    # CI should fail only for broken internal targets. Canonical/orphan findings
    # are advisory because some intentional landing pages may have no HTML links.
    if broken:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
