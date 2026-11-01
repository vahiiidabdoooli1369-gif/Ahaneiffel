#!/usr/bin/env python3
"""Create a transparent, heuristic on-page readiness report for Ahaneiffel HTML pages.

This is an internal triage score, NOT Google's ranking score or a prediction of rankings.
It checks observable HTML implementation signals only; Search Console and human review
are required to assess demand, usefulness, trust, performance, and actual search outcomes.
"""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
import csv
import json
import re

ROOT = Path(".")
OUT = ROOT / "agent-reports"
OUT.mkdir(exist_ok=True)
BASE = "https://ahaneiffel.top"

def clean_text(value):
    value = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()

def attr(tag, name):
    match = re.search(r"\b" + re.escape(name) + r"\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
    return unescape(match.group(2).strip()) if match else ""

class PageSignals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.h1 = []
        self.in_h1 = False
        self.h1_current = ""
        self.links = []
        self.images = []
        self.jsonld = []
        self.in_jsonld = False
        self.jsonld_current = ""
        self.headings = 0
        self.lang = ""
        self.canonical = ""
        self.description = ""
        self.robots = ""
        self.viewport = False
        self.og_title = False
        self.og_description = False
        self.word_count = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
            self.h1_current = ""
        elif tag in ("h2", "h3"):
            self.headings += 1
        elif tag == "a":
            self.links.append(a.get("href", ""))
        elif tag == "img":
            self.images.append(a.get("alt"))
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical = a.get("href", "")
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            prop = (a.get("property") or "").lower()
            if name == "description":
                self.description = a.get("content", "")
            elif name == "robots":
                self.robots = a.get("content", "").lower()
            elif name == "viewport":
                self.viewport = True
            if prop == "og:title":
                self.og_title = True
            elif prop == "og:description":
                self.og_description = True
        elif tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.jsonld_current = ""
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1" and self.in_h1:
            self.h1.append(self.h1_current.strip())
            self.in_h1 = False
        elif tag == "script" and self.in_jsonld:
            self.jsonld.append(self.jsonld_current)
            self.in_jsonld = False
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1_current += data
        if self.in_jsonld:
            self.jsonld_current += data

def evaluate(path):
    raw = path.read_text(encoding="utf-8", errors="ignore")
    p = PageSignals()
    try:
        p.feed(raw)
    except Exception:
        pass
    text = clean_text(raw)
    p.word_count = len(text.split())
    checks = []
    def add(label, passed, points, note=""):
        checks.append((label, bool(passed), points, note))
    add("title", bool(p.title.strip()), 10, "Missing or empty title")
    add("meta_description", bool(p.description.strip()), 10, "Missing or empty description")
    add("single_h1", len([x for x in p.h1 if x]) == 1, 10, "Expected exactly one non-empty H1")
    add("canonical", bool(p.canonical), 10, "Canonical not detected")
    add("canonical_host", p.canonical.startswith(BASE), 5, "Canonical should use primary HTTPS host")
    add("html_lang", bool(p.lang), 5, "HTML lang attribute missing")
    add("viewport", p.viewport, 5, "Viewport meta missing")
    add("content_depth_proxy", p.word_count >= 250, 10, f"Only {p.word_count} visible-text words (human review required)")
    add("section_structure", p.headings >= 2, 5, "Fewer than two H2/H3 headings detected")
    internal = sum(1 for h in p.links if h.startswith("/") or h.startswith(BASE))
    add("internal_links", internal >= 2, 10, f"Only {internal} internal links detected")
    add("image_alt", all((alt or "").strip() for alt in p.images), 5, "One or more images lack alt text")
    schema_ok = False
    if p.jsonld:
        try:
            for block in p.jsonld:
                json.loads(block)
            schema_ok = True
        except Exception:
            schema_ok = False
    add("jsonld_valid", schema_ok, 10, "No valid JSON-LD detected (may be inapplicable)")
    add("robots_indexable", "noindex" not in p.robots, 5, "Robots meta contains noindex")
    add("open_graph", p.og_title and p.og_description, 5, "OG title/description incomplete")
    score = sum(points for _, passed, points, _ in checks if passed)
    issues = [note for _, passed, _, note in checks if not passed and note]
    return {
        "url": BASE + "/" + str(path).replace("\\", "/").lstrip("./"),
        "file": str(path),
        "score": score,
        "band": "Strong implementation" if score >= 85 else "Needs improvement" if score >= 65 else "High-priority review",
        "word_count_proxy": p.word_count,
        "internal_links": internal,
        "h1_count": len([x for x in p.h1 if x]),
        "issues": "; ".join(issues[:8]),
    }

rows = []
for path in sorted(ROOT.rglob("*.html")):
    if ".git" in path.parts or path.name.lower() == "404.html":
        continue
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<!doctype\s+html|<html\b", raw, re.I):
        continue
    rows.append(evaluate(path))

rows.sort(key=lambda row: (row["score"], row["url"]))
csv_path = OUT / "page-readiness.csv"
with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["url", "file", "score", "band", "word_count_proxy", "internal_links", "h1_count", "issues"])
    writer.writeheader()
    writer.writerows(rows)

md = [
    "# Ahaneiffel page readiness report",
    "",
    "> Internal heuristic for prioritizing manual review. This is NOT a Google score, ranking factor, content-quality verdict, or traffic forecast.",
    "",
    f"- HTML pages assessed: {len(rows)}",
    f"- Mean implementation score: {sum(r['score'] for r in rows) / len(rows):.1f}/100" if rows else "- Mean implementation score: n/a",
    f"- Pages below 65: {sum(r['score'] < 65 for r in rows)}",
    "",
    "## Highest-priority pages to review",
    "",
]
for row in rows[:30]:
    md += [f"### {row['score']}/100 — {row['url']}", f"- Status: {row['band']}", f"- Review signals: {row['issues'] or 'No missing signals detected by this limited checker.'}", ""]
md += ["## Important limitations", "", "- Does not measure Google rankings, query demand, CTR, backlinks, Core Web Vitals, rendered JavaScript, or actual indexing.", "- Word count and schema presence are weak proxies; longer pages are not automatically better and every page does not need every schema type.", "- Use Search Console data and human editorial review before changing a page.", ""]
(OUT / "page-readiness.md").write_text("\n".join(md), encoding="utf-8")
print(f"PASS: assessed {len(rows)} HTML pages; mean heuristic score {sum(r['score'] for r in rows) / len(rows):.1f}/100" if rows else "WARN: no standalone HTML pages found")
print(f"Reports: {OUT / 'page-readiness.md'} and {csv_path}")
