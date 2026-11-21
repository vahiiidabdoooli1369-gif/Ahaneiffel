#!/usr/bin/env python3
"""Read-only guard for numeric quote cells: every displayed price needs an explicit date and status."""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".github", "node_modules"}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
DATE_RE = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
NUMBER_RE = re.compile(r"\d[\d,٬]*(?:\.\d+)?")

class QuoteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = []
        self.active = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = {k.lower(): v for k, v in attrs if k}
        classes = (attrs.get("class") or "").split()
        if self.active is None and tag.lower() in {"td", "th", "span", "strong"} and "quote" in classes:
            self.active = {"tag": tag.lower(), "date": attrs.get("data-price-date"), "status": attrs.get("data-price-status"), "source": attrs.get("data-price-source"), "verified": attrs.get("data-price-verified"), "text": ""}
            self.depth = 1
        elif self.active is not None:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.active is None:
            return
        self.depth -= 1
        if self.depth <= 0:
            self.cells.append(self.active)
            self.active = None
            self.depth = 0

    def handle_data(self, data):
        if self.active is not None:
            self.active["text"] += data

def inspect_cell(cell: dict) -> list[str]:
    text = " ".join(cell.get("text", "").split())
    if not NUMBER_RE.search(text.translate(DIGITS)):
        return []
    issues = []
    price_date = (cell.get("date") or "").strip().translate(DIGITS)
    if not DATE_RE.fullmatch(price_date):
        issues.append("numeric-price-missing-valid-date")
    else:
        try:
            year, month, day = map(int, re.split(r"[-/]", price_date))
            if year < 1300 or not 1 <= month <= 12 or not 1 <= day <= 31:
                issues.append("numeric-price-invalid-date")
        except ValueError:
            issues.append("numeric-price-invalid-date")
    status = (cell.get("status") or "").strip().lower()
    if status not in {"historical", "verified"}:
        issues.append("numeric-price-missing-valid-status")
    if status == "verified" and (cell.get("verified") or "").strip().lower() != "true":
        issues.append("verified-price-missing-verification-flag")
    if status == "verified" and not (cell.get("source") or "").strip():
        issues.append("verified-price-missing-source")
    return issues

def inspect_page(path: Path) -> dict:
    parser = QuoteParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    findings = []
    for index, cell in enumerate(parser.cells, 1):
        issues = inspect_cell(cell)
        if issues:
            findings.append({"cell_index": index, "text": " ".join(cell["text"].split()), "date": cell.get("date"), "status": cell.get("status"), "issues": issues})
    return {"path": path.relative_to(ROOT).as_posix(), "quote_cells": len(parser.cells), "numeric_quote_cells": sum(bool(NUMBER_RE.search(" ".join(c["text"].split()).translate(DIGITS))) for c in parser.cells), "findings": findings}

def audit(paths):
    pages = [inspect_page(p) for p in paths]
    counts = Counter(issue for page in pages for row in page["findings"] for issue in row["issues"])
    return {"page_count": len(pages), "quote_cells": sum(p["quote_cells"] for p in pages), "numeric_quote_cells": sum(p["numeric_quote_cells"] for p in pages), "finding_count": sum(len(p["findings"]) for p in pages), "issue_counts": dict(sorted(counts.items())), "pages": pages}

def self_test():
    good = QuoteParser()
    good.feed('<table><tr><td class="quote" data-price-date="1405-08-27" data-price-status="historical">۱۱۶٬۰۰۰ تومان</td></tr></table>')
    assert len(good.cells) == 1 and good.cells[0]["status"] == "historical"
    bad = QuoteParser()
    bad.feed('<td class="quote">۱۱۶٬۰۰۰ تومان</td>')
    cell = bad.cells[0]
    assert not cell["date"] and not cell["status"]
    verified = QuoteParser()
    verified.feed('<td class="quote" data-price-date="1405-08-30" data-price-status="verified" data-price-verified="true" data-price-source="کارشناس">۱۱۶٬۰۰۰</td>')
    assert verified.cells[0]["verified"] == "true" and verified.cells[0]["source"] == "کارشناس"
    text_only = QuoteParser()
    text_only.feed('<td class="quote">استعلام روز</td>')
    assert not NUMBER_RE.search(text_only.cells[0]["text"].translate(DIGITS))
    print("Price display audit self-test passed (4 assertions).")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/price-display-audit.json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    paths = sorted(p for p in ROOT.rglob("*.html") if not any(part in SKIP for part in p.parts) and ("price" in p.as_posix().lower() or "قیمت" in p.as_posix()))
    report = audit(paths)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Price-related HTML pages audited: {report['page_count']}")
    print(f"Numeric quote cells: {report['numeric_quote_cells']}")
    print(f"Price display findings: {report['finding_count']}")
    for key, value in report["issue_counts"].items():
        print(f"{key}: {value}")
    print(f"JSON report: {out}")
    return 1 if report["finding_count"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
