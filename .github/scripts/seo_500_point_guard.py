#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import json,re,sys
from urllib.parse import urlparse

ROOT=Path(".")
BASE="https://ahaneiffel.top"
pages=sorted(ROOT.rglob("index.html"))
ignore={"node_modules",".git",".next","dist","build"}
pages=[p for p in pages if not any(x in p.parts for x in ignore)]

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags=[]; self.attrs=[]; self.text=[]; self.links=[]; self.images=[]; self.h1=0; self.title=""; self.in_title=False
    def handle_starttag(self,t,a):
        d=dict(a); self.tags.append(t); self.attrs.append((t,d))
        if t=="a" and d.get("href"): self.links.append(d["href"])
        if t=="img": self.images.append(d)
        if t=="h1": self.h1+=1
        if t=="title": self.in_title=True
    def handle_endtag(self,t):
        if t=="title": self.in_title=False
    def handle_data(self,d):
        if self.in_title: self.title+=d
        self.text.append(d)

def checks(path,html):
    p=P()
    try: p.feed(html)
    except Exception as e: pass
    canon=re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',html,re.I)
    desc=re.findall(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)',html,re.I)
    viewport=re.search(r'<meta[^>]+name=["\']viewport["\']',html,re.I)
    lang=re.search(r'<html[^>]+lang=["\']([^"\']+)',html,re.I)
    json_blocks=re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html,re.I|re.S)
    schemas=[]; invalid=0
    for b in json_blocks:
        try:
            j=json.loads(b); schemas.append(j.get("@type") if isinstance(j,dict) else "")
        except: invalid+=1
    internal=[x for x in p.links if x.startswith("/") or x.startswith(BASE)]
    local=[]
    for x in internal:
        q=urlparse(x).path
        if q.startswith("/products/") and q.endswith("/"):
            local.append(q)
    unique_internal=len(set(internal))
    tests=[
      bool(re.search(r'<!doctype html',html,re.I)),
      bool(re.search(r'<html\b',html,re.I)), bool(re.search(r'</html>',html,re.I)),
      bool(re.search(r'<head\b',html,re.I)), bool(re.search(r'</head>',html,re.I)),
      bool(re.search(r'<body\b',html,re.I)), bool(re.search(r'</body>',html,re.I)),
      bool(re.search(r'<meta[^>]+charset=',html,re.I)), bool(viewport),
      bool(lang), bool(p.title.strip()), 10<=len(p.title.strip())<=75,
      len(desc)==1, 80<=len(desc[0])<=180 if desc else False,
      len(canon)==1, canon[0].startswith(BASE) if canon else False,
      canon[0].endswith("/") if canon else False,
      p.h1==1, len(internal)>=3, unique_internal>=3,
      len(set(p.links))>=len(p.links)*0.75 if p.links else False,
      all(i.get("alt") is not None for i in p.images),
      invalid==0, "BreadcrumbList" in schemas or path.name!="index.html",
      schemas.count("WebPage")<=1, "ProductGroup" not in schemas,
      not bool(re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex',html,re.I)),
    ]
    return tests, {"schemas":schemas,"invalid_jsonld":invalid,"canon":canon[:1],"h1":p.h1,"internal":len(internal),"unique_internal":unique_internal}

total=0;passed=0;critical=[]
rows=[]
for path in pages:
    html=path.read_text("utf-8",errors="replace")
    ts,meta=checks(path,html)
    total+=len(ts); passed+=sum(bool(x) for x in ts)
    if meta["invalid_jsonld"] or not meta["canon"] or meta["h1"]!=1:
        critical.append(str(path))
    rows.append((str(path),sum(bool(x) for x in ts),len(ts),meta))
report=ROOT/"seo-500-point-report.md"
with report.open("w",encoding="utf-8") as f:
    f.write("# Ahaneiffel 500+ Point SEO Guard\n\n")
    f.write(f"- HTML pages scanned: **{len(pages)}**\n- Checks executed: **{total}**\n- Passed: **{passed}**\n- Failed: **{total-passed}**\n- Critical files: **{len(critical)}**\n\n")
    f.write("## Per-page results\n\n|Page|Pass|Total|Schema|Invalid JSON-LD|Canonical|H1|Internal links|\n|---|---:|---:|---|---:|---|---:|---:|\n")
    for path,ok,n,m in rows:
        f.write(f"|{path}|{ok}|{n}|{','.join(map(str,m['schemas']))}|{m['invalid_jsonld']}|{m['canon'][0] if m['canon'] else '-'}|{m['h1']}|{m['unique_internal']}|\n")
    f.write("\n## Critical files\n")
    for x in critical[:200]: f.write(f"- {x}\n")
print(f"SCANNED={len(pages)} CHECKS={total} PASSED={passed} FAILED={total-passed} CRITICAL={len(critical)}")
# The guard is intentionally non-blocking while the site is being repaired in batches.
sys.exit(0)
