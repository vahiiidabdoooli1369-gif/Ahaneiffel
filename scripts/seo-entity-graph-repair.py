#!/usr/bin/env python3
"""Repair missing family-level entity links on product pages without changing prices."""
from pathlib import Path
import re

ROOT=Path(".")
required={
 "profile":("/prices/profile/","/guides/profile-price-today/"),
 "channel":("/prices/channel/","/guides/channel-light-vs-heavy/"),
 "rebar":("/prices/rebar/","/guides/rebar-price-vs-weight/"),
 "angle":("/prices/angle/","/guides/angle-size-selection/"),
 "beam":("/prices/beam/","/guides/beam-brand-size-price/"),
 "sheet":("/prices/sheet/","/guides/sheet-brand-size-price/"),
}
changed=0
for p in (ROOT/"products").glob("*/**/index.html"):
    rel=p.relative_to(ROOT/"products").as_posix()
    family=rel.split("/",1)[0]
    if family not in required: continue
    c=p.read_text(encoding="utf-8",errors="ignore")
    hrefs=set(re.findall(r'''href\s*=\s*["']([^"']+)["']''',c,re.I))
    missing=[x for x in required[family] if x not in hrefs and not any(x in h for h in hrefs)]
    if not missing: continue
    links=" | ".join(f'<a href="{x}">{x}</a>' for x in missing)
    block=f'<section class="entity-graph-links"><h2>منابع مرتبط با این محصول</h2><p>{links}</p></section>'
    if "</main>" not in c: continue
    p.write_text(c.replace("</main>",block+"</main>",1),encoding="utf-8")
    changed+=1
print(f"entity_graph_repaired={changed}")
