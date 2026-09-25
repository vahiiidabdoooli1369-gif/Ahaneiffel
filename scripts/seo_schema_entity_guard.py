from pathlib import Path
import json,re,sys
ROOT=Path("."); errors=[]; html_count=0; schema_count=0
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts or "node_modules" in p.parts: continue
    html_count+=1; s=p.read_text(encoding="utf-8",errors="ignore")
    blocks=re.findall(r'<script\s+type=["\']application/ld\+json["\']>([\s\S]*?)</script>',s,re.I)
    for b in blocks:
        try: data=json.loads(b)
        except Exception as e: errors.append(f"{p}: invalid JSON-LD: {e}"); continue
        schema_count+=1
        items=data if isinstance(data,list) else [data]
        for x in items:
            if not isinstance(x,dict): continue
            typ=x.get("@type")
            if typ=="Product":
                if not x.get("name"): errors.append(f"{p}: Product name missing")
                if not any(x.get(k) for k in ("offers","review","aggregateRating")): errors.append(f"{p}: incomplete Product entity")
            if "url" in x and isinstance(x["url"],str) and x["url"].startswith("http") and not x["url"].startswith("https://ahaneiffel.top/"):
                errors.append(f"{p}: schema url outside primary domain: {x['url']}")
            if x.get("mainEntityOfPage") and isinstance(x["mainEntityOfPage"],dict):
                u=x["mainEntityOfPage"].get("@id") or x["mainEntityOfPage"].get("url")
                if isinstance(u,str) and u.startswith("http") and not u.startswith("https://ahaneiffel.top/"):
                    errors.append(f"{p}: mainEntityOfPage outside primary domain")
print(f"Schema entity guard: {html_count} HTML files / {schema_count} JSON-LD blocks")
if errors:
    for e in errors[:200]: print("ERROR",e)
    sys.exit(1)
print("PASS: JSON-LD entities are syntactically valid and domain-consistent.")
