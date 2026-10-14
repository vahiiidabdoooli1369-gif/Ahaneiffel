#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urljoin, urlparse
import json, re, sys

ROOT = Path(".")
BASE = "https://ahaneiffel.top"
pages = sorted(ROOT.rglob("index.html"))
ignore = {"node_modules", ".git", ".next", "dist", "build"}
pages = [p for p in pages if not any(x in p.parts for x in ignore)]

CHECK_NAMES = [
    "doctype", "html_open", "html_close", "head_open", "head_close",
    "body_open", "body_close", "charset", "viewport", "html_lang",
    "title_present", "title_length_10_75", "single_meta_description",
    "description_length_80_180", "single_canonical",
    "canonical_on_expected_host", "canonical_trailing_slash", "exactly_one_h1",
    "at_least_3_internal_links", "at_least_3_unique_internal_links",
    "links_unique_ratio_75pct", "all_images_have_alt", "jsonld_valid",
    "homepage_breadcrumb_schema", "max_one_webpage_schema",
    "no_productgroup_schema", "not_noindex"
]

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs = []
        self.links = []
        self.images = []
        self.h1 = 0
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        self.attrs.append((tag, data))
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "img":
            self.images.append(data)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

def parse_page(html):
    parser = P()
    try:
        parser.feed(html)
    except Exception:
        pass
    return parser

def canonical_urls(parser):
    return [
        attrs.get("href", "")
        for tag, attrs in parser.attrs
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split() and attrs.get("href")
    ]

def redirect_info(path, html, parser):
    robots_noindex = any(
        tag == "meta" and attrs.get("name", "").lower() == "robots"
        and "noindex" in attrs.get("content", "").lower()
        for tag, attrs in parser.attrs
    )
    refresh_target = None
    for tag, attrs in parser.attrs:
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"""url\s*=\s*['"]?([^;'"]+)""", attrs.get("content", ""), re.I)
            if match:
                refresh_target = match.group(1).strip()
                break
    js_match = re.search(r"""location\.(?:replace|assign)\(\s*['"]([^'"]+)['"]\s*\)""", html, re.I)
    target = refresh_target or (js_match.group(1).strip() if js_match else None)
    is_stub = bool(robots_noindex and target)
    canon = canonical_urls(parser)
    if not is_stub:
        return None
    source_dir = path.parent.as_posix()
    base_url = BASE + "/" if source_dir == "." else BASE + "/" + source_dir.strip("/") + "/"
    target_url = urljoin(base_url, target)
    canonical_url = canon[0] if len(canon) == 1 else ""
    target_path = urlparse(target_url).path.rstrip("/") or "/"
    canonical_path = urlparse(canonical_url).path.rstrip("/") or "/" if canonical_url else ""
    valid = bool(target and len(canon) == 1 and urlparse(target_url).netloc == urlparse(BASE).netloc
                 and urlparse(canonical_url).netloc == urlparse(BASE).netloc
                 and target_path == canonical_path)
    return {"target": target, "resolved_target": target_url, "canonical": canonical_url, "valid": valid}

def checks(path, html, p):
    canon = canonical_urls(p)
    desc = [
        attrs.get("content", "")
        for tag, attrs in p.attrs
        if tag == "meta" and attrs.get("name", "").lower() == "description"
    ]
    viewport = any(tag == "meta" and "viewport" in attrs.get("name", "").lower() for tag, attrs in p.attrs)
    lang = next((attrs.get("lang", "") for tag, attrs in p.attrs if tag == "html"), "")
    charset = any(tag == "meta" and attrs.get("charset") for tag, attrs in p.attrs)
    robots_noindex = any(
        tag == "meta" and attrs.get("name", "").lower() == "robots"
        and "noindex" in attrs.get("content", "").lower()
        for tag, attrs in p.attrs
    )
    json_blocks = re.findall(r"""<script\b[^>]*type\s*=\s*["']application/ld\+json["'][^>]*>(.*?)</script>""", html, re.I | re.S)
    schemas = []
    invalid = 0
    for block in json_blocks:
        try:
            obj = json.loads(block)
            if isinstance(obj, dict):
                schemas.extend(obj.get("@type", []) if isinstance(obj.get("@type"), list) else [obj.get("@type", "")])
            else:
                invalid += 1
        except Exception:
            invalid += 1
    internal = [x for x in p.links if x.startswith("/") or x.startswith(BASE)]
    unique_internal = len(set(internal))
    is_homepage = path == ROOT / "index.html"
    tests = [
        bool(re.search(r"<!doctype html", html, re.I)),
        bool(re.search(r"<html\b", html, re.I)),
        bool(re.search(r"</html>", html, re.I)),
        bool(re.search(r"<head\b", html, re.I)),
        bool(re.search(r"</head>", html, re.I)),
        bool(re.search(r"<body\b", html, re.I)),
        bool(re.search(r"</body>", html, re.I)),
        charset, viewport, bool(lang), bool(p.title.strip()),
        10 <= len(p.title.strip()) <= 75,
        len(desc) == 1,
        80 <= len(desc[0]) <= 180 if desc else False,
        len(canon) == 1,
        urlparse(canon[0]).netloc == urlparse(BASE).netloc if canon else False,
        urlparse(canon[0]).path.endswith("/") if canon else False,
        p.h1 == 1, len(internal) >= 3, unique_internal >= 3,
        len(set(p.links)) >= len(p.links) * 0.75 if p.links else False,
        all(img.get("alt") is not None for img in p.images),
        invalid == 0,
        ("BreadcrumbList" in schemas) if is_homepage else True,
        schemas.count("WebPage") <= 1,
        "ProductGroup" not in schemas,
        not robots_noindex,
    ]
    failed = [name for name, ok in zip(CHECK_NAMES, tests) if not ok]
    return tests, {
        "schemas": schemas, "invalid_jsonld": invalid, "canon": canon[:1],
        "h1": p.h1, "unique_internal": unique_internal, "failed_checks": failed
    }

total = 0
passed = 0
critical = []
rows = []
redirect_rows = []
failure_counts = Counter()
for path in pages:
    html = path.read_text("utf-8", errors="replace")
    parser = parse_page(html)
    redirect = redirect_info(path, html, parser)
    if redirect:
        redirect_rows.append((str(path), redirect))
        continue
    tests, meta = checks(path, html, parser)
    total += len(tests)
    passed += sum(bool(x) for x in tests)
    failure_counts.update(meta["failed_checks"])
    if meta["invalid_jsonld"] or not meta["canon"] or meta["h1"] != 1:
        critical.append(str(path))
    rows.append((str(path), sum(bool(x) for x in tests), len(tests), meta))

report = ROOT / "seo-500-point-report.md"
with report.open("w", encoding="utf-8") as f:
    f.write("# Ahaneiffel 500+ Point SEO Guard\n\n")
    f.write(f"- HTML files discovered: **{len(pages)}**\n- Redirect stubs separately audited: **{len(redirect_rows)}**\n- Content pages audited: **{len(rows)}**\n- Checks executed on content pages: **{total}**\n- Passed: **{passed}**\n- Failed: **{total-passed}**\n- Critical content pages: **{len(critical)}**\n\n")
    f.write("## Failed checks by category (content pages only)\n\n|Check|Failures|\n|---|---:|\n")
    for name, count in failure_counts.most_common():
        f.write(f"|{name}|{count}|\n")
    f.write("\n## Redirect stubs\n\n|File|Target|Canonical|Redirect/canonical match|\n|---|---|---|---|\n")
    for path, info in redirect_rows:
        f.write(f"|{path}|{info['resolved_target']}|{info['canonical'] or '-'}|{'PASS' if info['valid'] else 'CHECK'}|\n")
    f.write("\n## Content page results\n\n|Page|Pass|Total|Failed checks|Schema types|Invalid JSON-LD|Canonical|H1|Unique internal links|\n|---|---:|---:|---|---|---:|---|---:|---:|\n")
    for path, ok, count, meta in rows:
        failed = ", ".join(meta["failed_checks"]) or "—"
        f.write(f"|{path}|{ok}|{count}|{failed}|{','.join(map(str, meta['schemas']))}|{meta['invalid_jsonld']}|{meta['canon'][0] if meta['canon'] else '-'}|{meta['h1']}|{meta['unique_internal']}|\n")
    f.write("\n## Critical content pages\n")
    for path in critical[:200]:
        f.write(f"- {path}\n")

print(f"FILES={len(pages)} REDIRECT_STUBS={len(redirect_rows)} CONTENT_PAGES={len(rows)} CHECKS={total} PASSED={passed} FAILED={total-passed} CRITICAL={len(critical)}")
print("FAILURE_BREAKDOWN:")
for name, count in failure_counts.most_common():
    print(f"  {name}={count}")
print("REDIRECT_STUB_AUDIT:")
for path, info in redirect_rows:
    if not info["valid"]:
        print(f"  CHECK {path} target={info['resolved_target']} canonical={info['canonical'] or '-'}")
print("PRIORITY_FAILURE_PATHS:")
for category in ("not_noindex", "canonical_trailing_slash", "title_length_10_75", "description_length_80_180", "html_close", "max_one_webpage_schema", "no_productgroup_schema", "homepage_breadcrumb_schema"):
    matched = [(path, meta["failed_checks"]) for path, _, _, meta in rows if category in meta["failed_checks"]]
    if matched:
        print(f"  [{category}] {len(matched)} page(s)")
        for path, _ in matched[:100]:
            print(f"    {path}")
print("TOP_FAILED_CONTENT_PAGES:")
for path, ok, count, meta in sorted(rows, key=lambda row: row[2]-row[1], reverse=True)[:30]:
    failed = ", ".join(meta["failed_checks"]) or "none"
    print(f"  {path} | failures={count-ok} | {failed}")
print("CRITICAL_CONTENT_PAGES:")
for path in critical[:200]:
    print(f"  {path}")
# Keep non-blocking while batches of verified fixes are applied.
sys.exit(0)
