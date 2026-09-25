#!/usr/bin/env python3
"""Audit product-family entity connections without inventing prices or schema."""
from pathlib import Path
from urllib.parse import urlparse

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
for p in PRODUCT.glob("*/**/index.html"):
    rel=p.relative_to(PRODUCT).as_posix()
    family=rel.split("/",1)[0]
    if family not in required_by_family: continue
    c=p.read_text(encoding="utf-8",errors="ignore")
    checked+=1
    if c.count('rel="canonical"')+c.count("rel='canonical'") != 1:
        errors.append(f"{p}: canonical count is not 1")
    for target in required_by_family[family]:
        if target not in c:
            errors.append(f"{p}: missing semantic link {target}")
    if "/prices/" not in c:
        errors.append(f"{p}: no price-intent link")
    if "/buy-iron/" not in c:
        errors.append(f"{p}: no purchase-intent link")
print(f"checked_product_pages={checked}")
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print("entity graph audit: PASS")
