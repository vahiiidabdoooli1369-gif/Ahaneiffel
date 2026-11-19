#!/usr/bin/env python3
"""Build a prioritized, non-mutating review queue from page-date-audit.json."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

def classify(path: str) -> tuple[int,str]:
    p=path.strip("/")
    if p.startswith("prices/") or p in {"price-center/index.html","market/index.html"}:
        return 1,"قیمت و استعلام"
    if p.startswith("products/"):
        depth=len(p.split("/"))
        return (2 if depth<=2 else 3),("صفحه مادر محصول" if depth<=2 else "صفحه محصول")
    if p in {"rebar/index.html","beam/index.html","profile/index.html","angle/index.html","channel/index.html"}:
        return 2,"هاب محصول"
    if p.startswith(("guides/","knowledge/")):
        return 4,"راهنما و محتوای آموزشی"
    if p.startswith("local/"):
        return 5,"صفحه محلی"
    if p.startswith(("reference/","tools/","search/")):
        return 6,"مرجع یا ابزار"
    if p.startswith(("about/","contact/","services/","buy-iron/")):
        return 3,"صفحه اعتماد و خدمات"
    return 7,"سایر"

def build(report: dict) -> dict:
    queue=[]
    for row in report.get("pages",[]):
        issues=row.get("issues",[])
        if not issues:
            continue
        rank,kind=classify(row.get("path",""))
        queue.append({
            "priority":rank,"type":kind,"path":row.get("path"),
            "last_content_change_tehran":row.get("last_content_change_tehran"),
            "expected_jalali_if_reviewed":row.get("expected_jalali"),
            "missing_structured_date":"missing-structured-date" in issues,
            "missing_visible_date":"missing-visible-date" in issues,
            "other_findings":[x for x in issues if x not in {"missing-structured-date","missing-visible-date"}],
            "review_status":"needs_human_content_review"
        })
    queue.sort(key=lambda x:(x["priority"],x["path"] or ""))
    counts=Counter(x["type"] for x in queue)
    priorities=Counter(str(x["priority"]) for x in queue)
    return {
        "source_page_count":report.get("page_count",0),
        "pages_needing_review":len(queue),
        "priority_counts":dict(sorted(priorities.items())),
        "type_counts":dict(sorted(counts.items())),
        "policy":"Do not add or change dates until a human verifies the page content. Git commit dates are hints, not proof of a substantive editorial review.",
        "queue":queue
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="artifacts/page-date-audit.json")
    ap.add_argument("--output",default="artifacts/page-date-review-queue.json")
    args=ap.parse_args()
    data=build(json.loads(Path(args.input).read_text(encoding="utf-8")))
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Pages needing human review: {data['pages_needing_review']}/{data['source_page_count']}")
    print("Priority counts: "+json.dumps(data["priority_counts"],ensure_ascii=False))
    print("Type counts: "+json.dumps(data["type_counts"],ensure_ascii=False))
    print(f"Review queue: {out}")

if __name__=="__main__":
    main()
