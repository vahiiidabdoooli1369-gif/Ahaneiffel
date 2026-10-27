#!/usr/bin/env python3
"""Static release audit for Ahaneiffel SEO, sitemap, schema and price-feed files.

Run from repository root: python scripts/seo_release_audit.py
No network calls are made; live HTTP/canonical checks belong to live-deployment-smoke.yml.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ahaneiffel.top"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
checks: list[tuple[str, bool, str]] = []


def check(name: str, passed: bool, detail: str = "") -> None:
    checks.append((name, bool(passed), detail))


def read(path: str) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError as exc:
        check(f"file readable: {path}", False, str(exc))
        return ""


def parse_xml(path: str):
    try:
        return ET.parse(ROOT / path).getroot()
    except (OSError, ET.ParseError) as exc:
        check(f"XML parses: {path}", False, str(exc))
        return None


# 1–12: required release files and homepage basics.
required = [
    "index.html", "style.css", "robots.txt", "sitemap.xml",
    "sitemap-core.xml", "sitemap-products.xml", "sitemap-guides.xml",
    "sitemap-reference.xml", "llms.txt", "data/market-prices.json",
    "assets/live-price-feed.js", ".github/workflows/live-deployment-smoke.yml",
]
for path in required:
    check(f"required file exists: {path}", (ROOT / path).is_file())

home = read("index.html")
robots = read("robots.txt")
llms = read("llms.txt")
css = read("style.css")
feed_text = read("data/market-prices.json")

title = re.search(r"<title[^>]*>(.*?)</title>", home, re.I | re.S)
description = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', home, re.I)
canonical = re.findall(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', home, re.I)
h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1\s*>", home, re.I | re.S)
check("homepage has non-empty title", bool(title and title.group(1).strip()))
check("homepage has non-empty meta description", bool(description and description.group(1).strip()))
check("homepage has exactly one canonical", len(canonical) == 1, f"count={len(canonical)}")
check("homepage canonical is the HTTPS homepage", canonical == [BASE + "/"], str(canonical))
check("homepage declares Persian language", bool(re.search(r'<html\b[^>]*lang=["\']fa["\']', home, re.I)))
check("homepage declares RTL direction", bool(re.search(r'<html\b[^>]*dir=["\']rtl["\']', home, re.I)))
check("homepage has exactly one H1", len(h1s) == 1, f"count={len(h1s)}")
check("homepage is indexable", bool(re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*index', home, re.I)))
check("homepage theme color is set", bool(re.search(r'<meta\s+name=["\']theme-color["\']', home, re.I)))
check("homepage includes a single JSON-LD block", home.count('type="application/ld+json"') == 1)
check("homepage CSS is linked", 'href="style.css"' in home)
check("homepage price feed script is linked", 'src="/assets/live-price-feed.js"' in home)
check("homepage avoids horizontal overflow at body level", "overflow-x:hidden" in css.replace(" ", ""))

# 13–24: parse structured data and verify the category URLs are discoverable.
jsonld_match = re.search(
    r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
    home, re.I | re.S
)
graph = []
jsonld_ok = False
if jsonld_match:
    try:
        schema = json.loads(jsonld_match.group(1))
        graph = schema.get("@graph", [])
        jsonld_ok = isinstance(graph, list) and bool(graph)
    except (json.JSONDecodeError, AttributeError):
        jsonld_ok = False
check("homepage JSON-LD parses as JSON", jsonld_ok)
types = {item.get("@type") for item in graph if isinstance(item, dict)}
for required_type in ("WholesaleStore", "WebSite", "WebPage", "ItemList"):
    check(f"JSON-LD contains {required_type}", required_type in types)
webpage = next((x for x in graph if isinstance(x, dict) and x.get("@type") == "WebPage"), {})
check("WebPage schema has URL", webpage.get("url") == BASE + "/")
check("WebPage schema has dateModified", bool(re.fullmatch(r"20\d\d-\d\d-\d\d", str(webpage.get("dateModified", "")))))
itemlist = next((x for x in graph if isinstance(x, dict) and x.get("@type") == "ItemList"), {})
items = itemlist.get("itemListElement", []) if isinstance(itemlist, dict) else []
item_urls = [x.get("url") for x in items if isinstance(x, dict) and x.get("url")]
check("product ItemList has at least 10 URL entries", len(item_urls) >= 10, f"count={len(item_urls)}")
check("product ItemList positions are sequential", [x.get("position") for x in items if isinstance(x, dict)] == list(range(1, len(items) + 1)))
check("product ItemList URLs are unique", len(item_urls) == len(set(item_urls)))
check("product ItemList URLs use HTTPS and the site domain", all(urlparse(u).scheme == "https" and urlparse(u).netloc == "ahaneiffel.top" for u in item_urls))

# 25–36: sitemap index, XML integrity and URL consistency.
index_root = parse_xml("sitemap.xml")
sitemap_files: list[str] = []
if index_root is not None:
    for node in index_root.findall("sm:sitemap/sm:loc", NS):
        url = (node.text or "").strip()
        parsed = urlparse(url)
        if parsed.netloc == "ahaneiffel.top" and parsed.path.rsplit("/", 1)[-1].endswith(".xml"):
            sitemap_files.append(parsed.path.rsplit("/", 1)[-1])
check("sitemap index references at least 10 sitemap files", len(sitemap_files) >= 10, f"count={len(sitemap_files)}")
check("sitemap index has no duplicate child sitemap URLs", len(sitemap_files) == len(set(sitemap_files)))
all_sitemap_urls: set[str] = set()
sitemap_parse_count = 0
for filename in sitemap_files:
    root = parse_xml(filename)
    if root is None:
        continue
    sitemap_parse_count += 1
    locs = [(node.text or "").strip() for node in root.findall(".//sm:loc", NS)]
    check(f"sitemap has URLs: {filename}", bool(locs))
    check(f"sitemap has unique URLs internally: {filename}", len(locs) == len(set(locs)))
    check(f"sitemap URLs use HTTPS site domain: {filename}",
          all(urlparse(u).scheme == "https" and urlparse(u).netloc == "ahaneiffel.top" for u in locs))
    for u in locs:
        all_sitemap_urls.add(u)
    for node in root.findall(".//sm:lastmod", NS):
        value = (node.text or "").strip()
        check(f"lastmod format in {filename}: {value}", bool(re.fullmatch(r"20\d\d-\d\d-\d\d", value)))
check("all indexed sitemap files parse", sitemap_parse_count == len(sitemap_files), f"parsed={sitemap_parse_count}, indexed={len(sitemap_files)}")
product_root = parse_xml("sitemap-products.xml")
product_urls = set()
if product_root is not None:
    product_urls = {(node.text or "").strip() for node in product_root.findall(".//sm:loc", NS)}
check("all JSON-LD product category URLs are in product sitemap", set(item_urls).issubset(product_urls),
      f"missing={sorted(set(item_urls) - product_urls)}")
check("homepage appears in core sitemap", BASE + "/" in {
    (n.text or "").strip() for n in (parse_xml("sitemap-core.xml") or ET.Element("root")).findall(".//sm:loc", NS)
})
check("robots.txt allows crawling", bool(re.search(r"(?im)^Allow:\s*/\s*$", robots)))
check("robots.txt references sitemap index", "https://ahaneiffel.top/sitemap.xml" in robots)

# 37–48: price feed, AI retrieval and key commercial links.
feed = {}
feed_ok = False
try:
    feed = json.loads(feed_text)
    feed_ok = isinstance(feed, dict)
except json.JSONDecodeError:
    feed_ok = False
check("price feed parses as JSON", feed_ok)
check("price feed has a published date", bool(feed.get("published_date")))
check("price feed declares currency", bool(feed.get("currency")))
rows = feed.get("rows", []) if isinstance(feed, dict) else []
check("price feed contains at least one row", isinstance(rows, list) and bool(rows))
check("price feed rows are objects", all(isinstance(row, dict) for row in rows))
check("price feed rows have a price field", all("price" in row for row in rows if isinstance(row, dict)))
check("price feed source is explicit", bool(feed.get("source")))
check("AI retrieval file exists and has a title", llms.lstrip().startswith("#"))
for fragment in ("https://ahaneiffel.top/", "prices/", "products/", "buy-iron/"):
    check(f"llms.txt references {fragment}", fragment in llms)
for path in (
    "/products/rebar/", "/products/beam/", "/products/profile/",
    "/products/angle/", "/products/channel/", "/products/sheet/",
):
    check(f"key product URL appears in sitemap index contents: {path}",
          BASE + path in all_sitemap_urls)
check("homepage includes business telephone", "09125143831" in home or "+989125143831" in home)
check("homepage contains a price center link", "prices/" in home or "price-center/" in home)
check("homepage contains product discovery links", "products/" in home)
check("price feed script has stale-data guard", "STALE_MS" in read("assets/live-price-feed.js"))
check("homepage has no empty title placeholder", bool(title and title.group(1).strip() not in ("", "Untitled")))

# 49–50: release metadata and report.
check("sitemap index and required product sitemap are present", "sitemap-products.xml" in sitemap_files)
check("source contains no accidental placeholder TODO in homepage", "TODO" not in home)

failed = [item for item in checks if not item[1]]
for name, passed, detail in checks:
    if not passed:
        print(f"FAIL | {name}" + (f" | {detail}" if detail else ""))
print(f"\nSEO release audit: {len(checks) - len(failed)}/{len(checks)} checks passed; {len(failed)} failed.")
if failed:
    sys.exit(1)
