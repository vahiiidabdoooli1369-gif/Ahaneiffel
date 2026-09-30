#!/usr/bin/env python3
import re,sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
SITE="https://ahaneiffel.top/"
htmls=[p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
titles=defaultdict(list); metas=defaultdict(list); cans=defaultdict(list)
issues=[]; zwnj=[]

for p in htmls:
    s=p.read_text(encoding="utf-8",errors="ignore")
    rel=p.relative_to(ROOT).as_posix()
    is_404=(rel=="404.html")
    is_noindex="noindex" in s.lower()

    if "‌" in s:
        zwnj.append(rel)

    m=re.search(r"<title>\s*(.*?)\s*</title>",s,re.I|re.S)
    if m and not is_noindex:
        titles[re.sub(r"\s+"," ",m.group(1)).strip()].append(rel)
    elif not m and not is_noindex:
        issues.append(f"NO_TITLE {rel}")

    m=re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',s,re.I)
    if m and not is_noindex and not is_404:
        metas[m.group(1).strip()].append(rel)
    elif not m and not is_noindex and not is_404:
        issues.append(f"NO_META_DESCRIPTION {rel}")

    m=re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',s,re.I)
    canonical=m.group(1).strip() if m else None
    if canonical:
        if not is_noindex and not is_404:
            cans[canonical].append(rel)
        if not canonical.startswith(SITE):
            issues.append(f"BAD_CANONICAL_HOST {rel} -> {canonical}")
    elif not is_noindex and not is_404:
        issues.append(f"NO_CANONICAL {rel}")

    h1=len(re.findall(r"<h1\b",s,re.I))
    if h1!=1 and not is_noindex and not is_404:
        issues.append(f"H1_COUNT {rel}={h1}")

    if "/assets/social-float.js" not in s and rel!="404.html":
        issues.append(f"NO_SOCIAL_FLOAT {rel}")

    if is_noindex and rel not in ("404.html","search/index.html"):
        has_redirect=("http-equiv="refresh" in s.lower()) or ("location.replace(" in s.lower())
        canonical_is_valid=bool(canonical and canonical.startswith(SITE))
        # A deliberate consolidation page may be noindex when its canonical points
        # to a different same-site URL. This is valid without a client-side redirect.
        canonical_points_elsewhere=bool(canonical_is_valid and canonical.rstrip("/") != (SITE+rel).rstrip("/"))
        if not (has_redirect or canonical_points_elsewhere):
            issues.append(f"NOINDEX_REVIEW {rel}")

for k,v in titles.items():
    if len(v)>1: issues.append("DUP_TITLE "+str(v))
for k,v in metas.items():
    if len(v)>1: issues.append("DUP_META "+str(v))
for k,v in cans.items():
    if len(v)>1: issues.append("DUP_CANONICAL "+k+" "+str(v))

sitemaps=list(ROOT.glob("sitemap*.xml"))
for sm in sitemaps:
    s=sm.read_text(encoding="utf-8",errors="ignore")
    locs=re.findall(r"<loc>(.*?)</loc>",s)
    if len(locs)!=len(set(locs)):
        issues.append(f"DUP_SITEMAP_LOC {sm.name}")
    for u in locs:
        if not u.startswith(SITE):
            issues.append(f"BAD_SITEMAP_HOST {sm.name} {u}")

print(f"SEO health: {len(htmls)} HTML pages; {len(sitemaps)} sitemap files")
print(f"duplicate titles={sum(len(v)>1 for v in titles.values())}; duplicate metas={sum(len(v)>1 for v in metas.values())}; duplicate canonicals={sum(len(v)>1 for v in cans.values())}")
print(f"zwnj occurrences={len(zwnj)}")
for x in issues[:200]:
    print(x)
if issues or zwnj:
    print(f"TOTAL_ISSUES={len(issues)+len(zwnj)}")
    sys.exit(1)
print("SEO_HEALTH=PASS")
