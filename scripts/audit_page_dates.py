#!/usr/bin/env python3
"""Report page-date coverage and freshness without modifying site files."""
from __future__ import annotations
import argparse, json, re, subprocess
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".github", "node_modules"}
AUTO_COMMIT_PATTERNS = ("Sync page dates with last content changes", "[date-sync]", "Update all page and sitemap dates")
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ISO_RE = re.compile(r'"dateModified"\s*:\s*"([^"]+)"', re.I)
META_RE = re.compile(r'<meta\b(?=[^>]*(?:name|property)=["\'](?:dateModified|article:modified_time|last-modified)["\'])(?=[^>]*content=["\']([^"\']+)["\'])[^>]*>', re.I)
VISIBLE_RE = re.compile(
    r'(?:آخرین\s*(?:به[\s‌]*روزرسانی|بروزرسانی)|(?:به[\s‌]*روزرسانی|بروزرسانی)\s*(?:صفحه|محتوا|تاریخ)?|تاریخ\s*(?:آخرین\s*تغییر|به[\s‌]*روزرسانی)|Updated\s*:?)'
    r'\s*(?:[:：\-–]\s*)?(?:</[^>]+>\s*)?([۰-۹0-9]{4})[/\-年]([۰-۹0-9]{1,2})[/\-月]([۰-۹0-9]{1,2})',
    re.I,
)

def gregorian_to_jalali(value: date) -> str:
    gy, gm, gd = value.year, value.month, value.day
    g_months = [31,28,31,30,31,30,31,31,30,31,30,31]
    j_months = [31,31,31,31,31,31,30,30,30,30,30,29]
    gy -= 1600; gm -= 1; gd -= 1
    day_no = 365*gy + (gy+3)//4 - (gy+99)//100 + (gy+399)//400
    day_no += sum(g_months[:gm])
    if gm > 1 and ((value.year%4 == 0 and value.year%100 != 0) or value.year%400 == 0):
        day_no += 1
    day_no += gd
    j_no = day_no - 79
    j_np = j_no // 12053; j_no %= 12053
    jy = 979 + 33*j_np + 4*(j_no//1461); j_no %= 1461
    if j_no >= 366:
        jy += (j_no-1)//365; j_no = (j_no-1)%365
    jm = 0
    while jm < 11 and j_no >= j_months[jm]:
        j_no -= j_months[jm]; jm += 1
    return f"{jy:04d}/{jm+1:02d}/{j_no+1:02d}"

def last_content_date(path: Path) -> date | None:
    rel = path.relative_to(ROOT).as_posix()
    command = ["git","log","-1","--format=%cI","--no-renames","--invert-grep","--fixed-strings"]
    command += [f"--grep={pattern}" for pattern in AUTO_COMMIT_PATTERNS]
    command += ["--", rel]
    result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=False)
    if result.returncode or not result.stdout.strip():
        return None
    try:
        stamp = datetime.fromisoformat(result.stdout.strip().replace("Z","+00:00"))
        return stamp.astimezone(ZoneInfo("Asia/Tehran")).date()
    except ValueError:
        return None

def scan_page(path: Path) -> dict:
    source = path.read_text(encoding="utf-8",errors="replace")
    structured = [*ISO_RE.findall(source), *META_RE.findall(source)]
    visible = [f"{m.group(1).translate(PERSIAN_DIGITS)}/{int(m.group(2).translate(PERSIAN_DIGITS)):02d}/{int(m.group(3).translate(PERSIAN_DIGITS)):02d}" for m in VISIBLE_RE.finditer(source)]
    issues=[]
    parsed=[]
    for value in structured:
        try: parsed.append(date.fromisoformat(value[:10]))
        except ValueError: issues.append(f"invalid-structured-date:{value}")
    if not structured: issues.append("missing-structured-date")
    if not visible: issues.append("missing-visible-date")
    if len(set(structured)) > 1: issues.append("conflicting-structured-dates")
    if len(set(visible)) > 1: issues.append("conflicting-visible-dates")
    latest = last_content_date(path)
    expected_iso = latest.isoformat() if latest else None
    expected_jalali = gregorian_to_jalali(latest) if latest else None
    if latest and parsed and any(item != latest for item in parsed):
        issues.append("structured-date-differs-from-last-content-change")
    if latest and visible and any(item != expected_jalali for item in visible):
        issues.append("visible-date-differs-from-last-content-change")
    if latest and any(item > date.today() for item in parsed):
        issues.append("future-structured-date")
    return {"path":path.relative_to(ROOT).as_posix(),"structured_dates":structured,"visible_dates":visible,"last_content_change_tehran":expected_iso,"expected_jalali":expected_jalali,"issues":issues}

def self_test():
    assert gregorian_to_jalali(date(2026,11,19)) == "1405/08/28"
    assert gregorian_to_jalali(date(2026,10,31)) == "1405/08/09"
    sample = '<p>آخرین بازبینی محتوای این صفحه: ۱۴۰۵/۰۸/۲۸</p>'
    assert len(list(VISIBLE_RE.finditer(sample))) == 1
    html = '<meta name="dateModified" content="2026-11-19"><script>{"dateModified":"2026-11-19"}</script>'
    assert ISO_RE.findall(html) == ["2026-11-19"]
    assert META_RE.findall(html) == ["2026-11-19"]
    print("Page-date audit self-test passed (5 assertions).")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="page-date-audit.json")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test(); return
    pages=sorted(p for p in ROOT.rglob("*.html") if not any(part in IGNORED_PARTS for part in p.parts))
    rows=[scan_page(p) for p in pages]
    counts={}
    for row in rows:
        for issue in row["issues"]: counts[issue]=counts.get(issue,0)+1
    report={"generated_at_utc":datetime.now().astimezone().isoformat(),"page_count":len(rows),"issue_counts":counts,"pages":rows}
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"HTML pages audited: {len(rows)}")
    print(f"Pages with at least one finding: {sum(bool(row['issues']) for row in rows)}")
    for issue,count in sorted(counts.items()): print(f"{issue}: {count}")
    print(f"JSON report: {output}")

if __name__ == "__main__":
    main()
