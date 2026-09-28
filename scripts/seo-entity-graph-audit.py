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
errors=[]; warnings=[]; checked=0

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
        if target not in targets: warnings.append(f"{p}: missing supporting guide link {target}")
    if not any(x.startswith("/prices/") for x in targets): errors.append(f"{p}: no price-intent link")
    if not any(x.startswith("/buy-iron/") for x in targets): errors.append(f"{p}: no purchase-intent link")
    products=re.findall(r'"@type"\\s*:\\s*"Product"([\\s\\S]*?)\\}',c,re.I)
    if not products:
        warnings.append(f"{p}: no Product entity; structured Product schema is optional when no valid offer/review/rating is available")
    else:
        block=products[0]
        if '"name"' not in block: errors.append(f"{p}: Product has no name")
        if '"url"' not in block: errors.append(f"{p}: Product has no url")
        if '"brand"' not in block: errors.append(f"{p}: Product has no brand")
        if '"sku"' not in block: warnings.append(f"{p}: Product has no sku")
        if '"offers"' not in block and '"review"' not in block and '"aggregateRating"' not in block:
            warnings.append(f"{p}: Product has no offers/review/aggregateRating; price is not forced when no fixed price is published")
print(f"checked_product_pages={checked}")
print(f"warnings={len(warnings)}")
for w in warnings[:200]: print("WARNING", w)
if errors:
    print("\n".join(errors[:200])); print(f"total_errors={len(errors)}"); raise SystemExit(1)
print("entity graph audit: PASS")
