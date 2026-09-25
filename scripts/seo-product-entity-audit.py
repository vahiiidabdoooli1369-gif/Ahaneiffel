from pathlib import Path
import json,re,html

ROOT=Path(__file__).resolve().parents[1]
pages=[p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
errors=[]; warnings=[]

for p in pages:
    s=p.read_text(encoding="utf-8",errors="ignore")
    if "/products/" not in p.as_posix(): continue
    cans=re.findall(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',s,re.I)
    if len(cans)!=1: errors.append(f"{p}: canonical count={len(cans)}")
    for block in re.findall(r'<script[^>]+type=["\']application/ld\\+json["\'][^>]*>(.*?)</script>',s,re.I|re.S):
        try:
            data=json.loads(html.unescape(block))
        except Exception:
            errors.append(f"{p}: invalid JSON-LD"); continue
        nodes=data.get("@graph",[data]) if isinstance(data,dict) else []
        for n in nodes:
            if isinstance(n,dict) and n.get("@type")=="Product":
                if not any(k in n for k in ("offers","review","aggregateRating")):
                    errors.append(f"{p}: Product without offers/review/aggregateRating")
    for href in re.findall(r'<a\b[^>]+href=["\']([^"\']+)["\']',s,re.I):
        if href.startswith(("http://","https://","/","#","tel:","mailto:")): continue
        target=(p.parent/href).resolve()
        if target.is_dir(): target=target/"index.html"
        if target.suffix=="" and (target/"index.html").is_file(): target=target/"index.html"
        if not target.exists(): warnings.append(f"{p}: broken relative link {href}")

print(f"product-pages={sum('/products/' in p.as_posix() for p in pages)}")
print(f"errors={len(errors)} warnings={len(warnings)}")
for x in errors[:200]: print("ERROR",x)
for x in warnings[:200]: print("WARNING",x)
raise SystemExit(1 if errors else 0)
