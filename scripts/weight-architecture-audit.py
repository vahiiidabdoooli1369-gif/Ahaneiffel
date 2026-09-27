#!/usr/bin/env python3
"""20-point audit for the steel-weight content architecture."""
from pathlib import Path
import re
ROOT=Path(".")
GUIDES=ROOT/"guides"
PRODUCTS=ROOT/"products"
required = {
 "angle": ["/guides/angle-weight-table/","/tools/steel-weight-calculator/","/prices/angle/"],
 "channel": ["/guides/channel-weight-table/","/tools/steel-weight-calculator/","/prices/channel/"],
 "beam": ["/guides/beam-weight-table/","/tools/steel-weight-calculator/","/prices/beam/"],
 "profile": ["/guides/profile-weight/","/tools/steel-weight-calculator/","/prices/profile/"],
 "rebar": ["/guides/rebar-weight/","/tools/steel-weight-calculator/","/prices/rebar/"],
 "sheet": ["/guides/sheet-weight-calculation/","/tools/sheet-weight-calculator/","/prices/sheet/"],
}
errors=[]; warnings=[]
def html(p): return p.read_text(encoding="utf-8",errors="ignore")
def has(h, x): return x in h
def plain(h): return re.sub(r"\\s+"," ",re.sub(r"<[^>]+>"," ",h)).strip().lower()

# 1-6: family guide coverage
for family, links in required.items():
    guide = {"angle":"guides/angle-weight-table/index.html","channel":"guides/channel-weight-table/index.html",
             "beam":"guides/beam-weight-table/index.html","profile":"guides/profile-weight/index.html",
             "rebar":"guides/rebar-weight/index.html","sheet":"guides/sheet-weight-calculation/index.html"}[family]
    if not (ROOT/guide).exists(): errors.append(f"missing weight guide: {guide}"); continue
    h=html(ROOT/guide)
    for link in links:
        if not has(h, link): warnings.append(f"{guide}: missing {link}")

# 7-12: core calculation concepts
for p in [ROOT/x for x in ["guides/rebar-weight/index.html","guides/sheet-weight-calculation/index.html","guides/profile-weight/index.html","guides/beam-weight-table/index.html","guides/channel-weight-table/index.html","guides/angle-weight-table/index.html"]]:
    h=html(p); q=plain(h)
    for term in ["وزن","محاسبه","خرید"]:
        if term not in q: warnings.append(f"{p}: missing concept {term}")

# 13: calculator
calc=ROOT/"tools/steel-weight-calculator/index.html"
if calc.exists():
    q=plain(html(calc))
    for term in ["میلگرد","ورق","پروفیل","تیرآهن","نبشی","ناودانی"]:
        if term not in q: errors.append(f"calculator missing {term}")
else: errors.append("missing steel weight calculator")

# 14: reference hub
hub=ROOT/"reference/steel-weight-tables/index.html"
if not hub.exists(): errors.append("missing weight reference hub")
else:
    q=plain(html(hub))
    for term in ["میلگرد","تیرآهن","پروفیل","نبشی","ناودانی","ورق"]:
        if term not in q: errors.append(f"weight hub missing {term}")

# 15-20: product-family weight routes
for family in required:
    p=PRODUCTS/family/"index.html"
    if not p.exists(): warnings.append(f"missing family index: {p}"); continue
    h=html(p)
    for link in required[family]:
        if link not in h: warnings.append(f"{p}: missing weight route {link}")

print(f"errors={len(errors)} warnings={len(warnings)}")
for x in errors[:200]: print("ERROR",x)
for x in warnings[:200]: print("WARNING",x)
if errors: raise SystemExit(1)
print("weight architecture audit: PASS")
