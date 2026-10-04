from pathlib import Path
from urllib.parse import urlparse
import re,sys,xml.etree.ElementTree as ET

ROOT=Path("."); HOST="https://ahaneiffel.top"
errors=[]; warnings=[]

def file_for_url(u):
    parsed=urlparse(u); path=parsed.path
    if path in ("","/"): return ROOT/"index.html"
    path=path.lstrip("/")
    if path.endswith("/"): return ROOT/path/"index.html"
    return ROOT/path

seen_sitemap_urls=set()
sitemap_files=list(ROOT.glob("sitemap*.xml"))

sm=ROOT/"sitemap.xml"
if not sm.exists():
    errors.append("root sitemap.xml missing")
else:
    try:
        root=ET.parse(sm).getroot()
        for loc in root.findall(".//{*}loc"):
            u=(loc.text or "").strip()
            parsed=urlparse(u)
            if not (u==HOST or u.startswith(HOST+"/")):
                errors.append(f"sitemap index contains non-canonical host: {u}")
            if parsed.query or parsed.fragment:
                errors.append(f"sitemap index URL contains query/fragment: {u}")
            target=file_for_url(u)
            if target.suffix==".xml" and not target.exists():
                errors.append(f"sitemap child missing in repository: {u} -> {target}")
    except Exception as e:
        errors.append(f"invalid root sitemap: {e}")

for p in sitemap_files:
    try:
        root=ET.parse(p).getroot()
    except Exception as e:
        errors.append(f"{p}: invalid XML: {e}"); continue
    for loc in root.findall(".//{*}loc"):
        u=(loc.text or "").strip(); parsed=urlparse(u)
        if not (u==HOST or u.startswith(HOST+"/")):
            errors.append(f"{p}: non-canonical URL {u}")
        if parsed.query or parsed.fragment:
            errors.append(f"{p}: URL contains query/fragment {u}")
        if "%25" in u.lower():
            errors.append(f"{p}: double encoded URL {u}")
        if u in seen_sitemap_urls:
            errors.append(f"{p}: duplicate sitemap URL {u}")
        seen_sitemap_urls.add(u)
        target=file_for_url(u)
        if target.suffix==".xml":
            if not target.exists(): errors.append(f"{p}: missing child sitemap {u}")
        elif not target.exists():
            warnings.append(f"{p}: URL not mapped to repo file: {u}")

html=[p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts]
for p in html:
    s=p.read_text(encoding="utf-8",errors="ignore")
    robots=" ".join(re.findall(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)',s,re.I))
    noindex="noindex" in robots.lower() or p.name=="404.html"
    cs=re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*>',s,re.I)
    if not noindex and len(cs)!=1: errors.append(f"{p}: canonical count {len(cs)}")
    for c in cs:
        m=re.search(r'href=["\']([^"\']+)',c,re.I)
        if not m or not m.group(1).startswith(HOST+"/"):
            errors.append(f"{p}: canonical outside {HOST}")
    for u in re.findall(r'(?:href|src)=["\']([^"\']+)',s,re.I):
        if u.startswith("/") and ("%25" in u.lower() or "http://" in u.lower()):
            errors.append(f"{p}: malformed internal URL {u}")

for required in ["llms.txt","reference/ai-retrieval-map/index.html","robots.txt"]:
    if not (ROOT/required).exists(): errors.append(f"required AI/GEO asset missing: {required}")
if (ROOT/"robots.txt").exists():
    rb=(ROOT/"robots.txt").read_text(encoding="utf-8",errors="ignore")
    if "Sitemap: https://ahaneiffel.top/sitemap.xml" not in rb:
        errors.append("robots.txt sitemap directive missing")

print(f"Architecture guard: {len(html)} HTML files and {len(sitemap_files)} sitemaps checked; {len(seen_sitemap_urls)} unique sitemap URLs")
if warnings:
    print(f"WARNINGS {len(warnings)}")
    for x in warnings[:100]: print("WARN",x)
if errors:
    print(f"ERRORS {len(errors)}")
    for x in errors[:200]: print("ERROR",x)
    sys.exit(1)
print("PASS: sitemap, canonical, internal URL and AI/GEO architecture checks passed.")
