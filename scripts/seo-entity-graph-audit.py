#!/usr/bin/env python3
"""Audit product-family entity connections using normalized links."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import re, posixpath

ROOT=Path(".")
PRODUCT=ROOT/"products"
required_by_family={
 "profile":("/prices/profile/","/guides/profile-price-today/"),
 "channel":("/prices/channel/","/guides/channel-light-vs-heavy/"),
 "rebar":("/prices/rebar/","/guides/rebar-price-vs-weight/"),
 "angle":("/prices/angle/","/guides/angle-size-selection/"),
 "beam":("/prices/beam/","/guides/beam-brand-size-price/"),
 "sheet":("/prices/sheet/","/guides/sheet-brand-size-price/"),
}
errors=[]; checked=0

def site_path(href,page):
    href=unquote(href.strip())
    if not href or href.startswith(("#","mailto:","tel:","javascript:")): return ""
    if href.startswith("https://ahaneiffel.top"): return urlparse(href).path
    if href.startswith("/"): return href.split("#",1)[0].split("?",1)[0]
    if href.startswith(("http://","https://")): return ""
    base="/" + page.relative_to(ROOT).parent.as_posix() + "/"
    return posixpath.normpath(base + href.split("#",1)[0].split("?",1)[0])

for p in PRODUCT.glob("*/**/index.html"):
    rel=p.relative_to(PRODUCT).as_posix()
    family=rel.split("/",1)[0]
    if family not in required_by_family: continue
    c=p.read_text(encoding="utf-8",errors="ignore"); checked+=1
    if len(re.findall(r'<link[^>]+rel=["\']canonical["\']',c,re.I)) != 1:
        errors.append(f"{p}: canonical count is not 1")
    targets={site_path(h,p) for h in re.findall(r'''href\s*=\s*["']([^"']+)["']''',c,re.I)}
    targets.discard("")
    for target in required_by_family[family]:
        if target not in targets: errors.append(f"{p}: missing {target}")
    if not any(x.startswith("/prices/") for x in targets): errors.append(f"{p}: no price-intent link")
    if not any(x.startswith("/buy-iron/") for x in targets): errors.append(f"{p}: no purchase-intent link")
print(f"checked_product_pages={checked}")
if errors:
    print("\n".join(errors[:200])); print(f"total_errors={len(errors)}"); raise SystemExit(1)
print("entity graph audit: PASS")
