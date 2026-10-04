from pathlib import Path
import json,re,sys
from urllib.parse import urlparse
errors=[]; warnings=[]; checked=0; skipped=0
for path in Path('.').rglob('*.html'):
    if '.git' in path.parts: continue
    s=path.read_text(encoding='utf-8',errors='ignore')
    if not re.search(r'<!doctype\\s+html|<html\\b',s,re.I): skipped+=1; continue
    if re.search(r'<meta[^>]+name=["\\\']robots["\\\'][^>]+content=["\\\'][^"\\\']*noindex',s,re.I): skipped+=1; continue
    checked+=1
    canon=re.findall(r'<link[^>]+rel=["\\\']canonical["\\\'][^>]+href=["\\\']([^"\\\']+)',s,re.I)
    if not canon: errors.append(f'{path}: missing canonical')
    elif len(canon)>1: errors.append(f'{path}: multiple canonicals')
    for u in canon:
        if 'index.html' in u: errors.append(f'{path}: canonical contains index.html: {u}')
        if u.startswith('http') and urlparse(u).netloc not in {'ahaneiffel.top','www.ahaneiffel.top'}: errors.append(f'{path}: unexpected canonical host: {u}')
    for block in re.findall(r'<script[^>]+type=["\\\']application/ld\\+json["\\\'][^>]*>(.*?)</script>',s,re.I|re.S):
        try: json.loads(block)
        except Exception as e: errors.append(f'{path}: invalid JSON-LD: {e}')
        if 'index.html' in block: errors.append(f'{path}: JSON-LD contains index.html URL')
print(f'SEO integrity audit: {checked} indexable HTML documents checked; {skipped} fragments/noindex documents skipped')
for w in warnings[:100]: print('WARN',w)
for e in errors[:300]: print('ERROR',e)
if errors: sys.exit(1)
print('PASS: canonical and JSON-LD integrity checks passed.')
