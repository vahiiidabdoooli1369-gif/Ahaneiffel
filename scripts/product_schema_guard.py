from pathlib import Path
import json,re,sys

ROOT=Path(".")
errors=[]
product_pages=0

for p in ROOT.rglob("*.html"):
    if ".git" in p.parts or "node_modules" in p.parts: continue
    s=p.read_text(encoding="utf-8",errors="ignore")
    blocks=re.findall(r'<script\s+type=["\']application/ld\+json["\']>([\s\S]*?)</script>',s,re.I)
    for b in blocks:
        try: data=json.loads(b)
        except Exception as e:
            errors.append(f"{p}: invalid JSON-LD: {e}"); continue
        items=data if isinstance(data,list) else [data]
        for item in items:
            if not isinstance(item,dict): continue
            if item.get("@type")=="Product":
                product_pages += 1
                if not item.get("name"): errors.append(f"{p}: Product missing name")
                offers=item.get("offers")
                ratings=item.get("aggregateRating")
                reviews=item.get("review")
                if not offers and not ratings and not reviews:
                    errors.append(f"{p}: Product has none of offers/review/aggregateRating")
                if offers and isinstance(offers,dict):
                    if "price" not in offers:
                        errors.append(f"{p}: Product Offer missing price")
                    if offers.get("priceCurrency")!="IRR":
                        errors.append(f"{p}: Product Offer priceCurrency should be IRR")
print(f"Product schema guard: {product_pages} Product entities checked")
if errors:
    for e in errors[:200]: print("ERROR",e)
    sys.exit(1)
print("PASS: no invalid Product schema detected.")
