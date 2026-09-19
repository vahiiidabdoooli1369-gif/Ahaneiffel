from pathlib import Path
import re
from html import unescape

errors = []
warnings = []
seen_titles = {}
seen_canonicals = {}

for path in sorted(Path('.').rglob('index.html')):
    if any(part in {'.git', 'node_modules'} for part in path.parts):
        continue

    text = path.read_text(encoding='utf-8', errors='ignore')

    robots = re.search(
        r'<meta[^>]+name=["\\\']robots["\\\'][^>]+content=["\\\']([^"\\\']+)',
        text,
        re.I,
    )
    is_indexable = not robots or 'noindex' not in robots.group(1).lower()

    if not is_indexable:
        continue

    title = re.search(r'<title>(.*?)</title>', text, re.I | re.S)
    canonical = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',
        text,
        re.I,
    )
    h1s = re.findall(r'<h1\b[^>]*>(.*?)</h1>', text, re.I | re.S)

    if not title or not title.group(1).strip():
        errors.append(f'{path}: missing title')
    else:
        t = unescape(re.sub(r'<[^>]+>', ' ', title.group(1))).strip()
        seen_titles.setdefault(t, []).append(str(path))

    if not canonical:
        errors.append(f'{path}: missing canonical')
    else:
        c = canonical.group(1).strip()
        seen_canonicals.setdefault(c, []).append(str(path))
        if 'ahaneiffel.top' not in c or 'www.ahaneiffel.top' in c:
            errors.append(f'{path}: invalid canonical host {c}')

    if len(h1s) != 1:
        errors.append(f'{path}: expected 1 H1, found {len(h1s)}')

    # Persian ZWNJ (U+200C) is a valid typographic character and is not an SEO error.
    # Keep it allowed so legitimate Persian spelling does not fail CI.

    if (
        '<meta name="robots" content="noindex' not in text.lower()
        and path.parts[0] in {'products', 'guides', 'prices', 'local', 'reference'}
    ):
        visible = re.sub(
            r'<script.*?</script>|<style.*?</style>|<[^>]+>',
            ' ',
            text,
            flags=re.I | re.S,
        )
        words = re.findall(r'\S+', unescape(visible))
        if len(words) < 90:
            warnings.append(f'{path}: thin indexable content ({len(words)} tokens)')

for title, paths in seen_titles.items():
    if len(paths) > 1:
        warnings.append(
            'duplicate title candidate: ' + title + ' -> ' + ', '.join(paths)
        )

for canonical, paths in seen_canonicals.items():
    if len(paths) > 1:
        warnings.append(
            'duplicate canonical candidate: ' + canonical + ' -> ' + ', '.join(paths)
        )

if warnings:
    print('SEO intent audit warnings:')
    print('\n'.join(warnings))

if errors:
    print('SEO intent audit errors:')
    print('\n'.join(errors))
    raise SystemExit(1)

print('SEO intent audit passed: structural SEO checks are clean; warnings are non-blocking.')
