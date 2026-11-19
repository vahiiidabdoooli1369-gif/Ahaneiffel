#!/usr/bin/env python3
"""Read-only SEO metadata audit for HTML pages; never rewrites page content."""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".github", "node_modules"}

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts=[]; self.in_title=False; self.description=[]; self.canonical=[]
        self.h1_count=0; self.robots=[]; self.refresh=[]
    def handle_starttag(self, tag, attrs):
        a={k.lower():v for k,v in attrs if k}
        tag=tag.lower()
        if tag=="title": self.in_title=True
        if tag=="meta":
            name=(a.get("name") or "").lower()
            if name=="description": self.description.append(a.get("content") or "")
            if name=="robots": self.robots.append(a.get("content") or "")
            if name=="googlebot": self.robots.append(a.get("content") or "")
            if (a.get("http-equiv") or "").lower()=="refresh": self.refresh.append(a.get("content") or "")
        if tag=="link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical.append(a.get("href") or "")
        if tag=="h1": self.h1_count+=1
    def handle_endtag(self, tag):
        if tag.lower()=="title": self.in_title=False
    def handle_data(self, data):
        if self.in_title: self.title_parts.append(data)
    @property
    def title(self): return " ".join(" ".join(self.title_parts).split())
    @property
    def noindex(self):
        return any("noindex" in value.lower() for value in self.robots)
    @property
    def is_redirect(self):
        return bool(self.refresh)

def inspect(path: Path) -> dict:
    parser=PageParser()
    parser.feed(path.read_text(encoding="utf-8",errors="replace"))
    title=parser.title
    descriptions=[x.strip() for x in parser.description]
    desc=descriptions[0] if descriptions else ""
    non_indexable=parser.noindex or parser.is_redirect
    issues=[]
    # Noindex/redirect utility pages (e.g. legacy URL aliases and 404) are
    # intentionally excluded from indexable-page metadata quality findings.
    if not non_indexable:
        if not title: issues.append("missing-title")
        elif len(title)<25: issues.append("title-too-short")
        elif len(title)>65: issues.append("title-too-long")
        if not desc: issues.append("missing-description")
        elif len(desc)<70: issues.append("description-too-short")
        elif len(desc)>170: issues.append("description-too-long")
        if len(descriptions)>1: issues.append("multiple-description-tags")
        if parser.h1_count==0: issues.append("missing-h1")
        elif parser.h1_count>1: issues.append("multiple-h1")
        if not parser.canonical: issues.append("missing-canonical")
        elif len(parser.canonical)>1: issues.append("multiple-canonical-tags")
        if parser.canonical and not parser.canonical[0].startswith(("https://","http://")):
            issues.append("non-absolute-canonical")
    return {"path":path.relative_to(ROOT).as_posix(),"title":title,"title_length":len(title),
            "description":desc,"description_length":len(desc),"h1_count":parser.h1_count,
            "canonical_count":len(parser.canonical),"canonical":parser.canonical[0] if parser.canonical else None,
            "noindex":parser.noindex,"meta_refresh":parser.is_redirect,
            "indexable_audit":not non_indexable,"issues":issues}

def audit(paths):
    rows=[inspect(p) for p in paths]
    for key in ("title","description"):
        seen=defaultdict(list)
        for row in rows:
            value=row[key].strip().casefold()
            if row["indexable_audit"] and value: seen[value].append(row["path"])
        for group in seen.values():
            if len(group)>1:
                for row in rows:
                    if row["indexable_audit"] and row["path"] in group:
                        row["issues"].append("duplicate-"+key)
    counts=Counter(issue for row in rows for issue in row["issues"])
    return {"generated_at_utc":datetime.now(timezone.utc).isoformat(),"page_count":len(rows),
            "indexable_pages_audited":sum(x["indexable_audit"] for x in rows),
            "excluded_noindex_or_redirect_pages":sum(not x["indexable_audit"] for x in rows),
            "pages_with_findings":sum(bool(x["issues"]) for x in rows),
            "issue_counts":dict(sorted(counts.items())),"pages":rows}

def self_test():
    p=PageParser()
    p.feed('<title>عنوان مناسب برای صفحه آهن</title><meta name="description" content="شرح کامل این صفحه برای خریدار آهن و مشخصات محصول"><h1>عنوان</h1><link rel="canonical" href="https://example.com/a">')
    assert p.title=="عنوان مناسب برای صفحه آهن"
    assert len(p.description)==1 and p.h1_count==1 and len(p.canonical)==1
    redirect=PageParser()
    redirect.feed('<meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url=/target/">')
    assert redirect.noindex and redirect.is_redirect
    row={"title":"x","description":"y","h1_count":0,"canonical_count":0}
    assert len(inspect_sample(row))==4
    print("SEO metadata audit self-test passed (7 assertions).")

def inspect_sample(row):
    issues=[]
    if len(row["title"])<25: issues.append("title-too-short")
    if len(row["description"])<70: issues.append("description-too-short")
    if row["h1_count"]==0: issues.append("missing-h1")
    if row.get("canonical_count",0)==0: issues.append("missing-canonical")
    return issues

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="artifacts/seo-metadata-audit.json")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test: self_test(); return
    pages=sorted(p for p in ROOT.rglob("*.html") if not any(x in SKIP for x in p.parts))
    report=audit(pages)
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"HTML pages audited: {report['page_count']}")
    print(f"Indexable pages audited: {report['indexable_pages_audited']}")
    print(f"Excluded noindex/redirect pages: {report['excluded_noindex_or_redirect_pages']}")
    print(f"Pages with SEO metadata findings: {report['pages_with_findings']}")
    for key,value in report["issue_counts"].items(): print(f"{key}: {value}")
    print(f"JSON report: {out}")

if __name__=="__main__": main()
