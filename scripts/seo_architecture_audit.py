#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys
import xml.etree.ElementTree as ET

HOST = "ahaneiffel.top"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
REQUIRED = [
    "/",
    "/products/",
    "/products/rebar/",
    "/products/beam/",
    "/products/profile/",
    "/products/angle/",
    "/products/channel/",
    "/prices/",
    "/guides/",
    "/knowledge/",
    "/reference/",
    "/reference/ai-retrieval-map/",
    "/tools/",
    "/services/",
    "/buy-iron/",
    "/local/tehran/",
]
INTENT_HINTS = {
    "price": ["/prices/"],
    "product": ["/products/"],
    "guide": ["/guides/"],
    "knowledge": ["/knowledge/"],
    "reference": ["/reference/"],
}

def fail(msg):
    errors.append(msg)

errors, warnings = [], []
sitemap_urls = []
sitemap_files = ["sitemap.xml"]

try:
    root = ET.parse("sitemap.xml").getroot()
    if root.tag != f"{{{NS['sm']}}}sitemapindex":
        fail("sitemap.xml is not a sitemap index")
    for loc in root.findall("sm:sitemap/sm:loc", NS):
        if loc.text:
            u = loc.text.strip()
            sitemap_urls.append(u)
            path = urlparse(u).path.lstrip("/")
            if not path.endswith(".xml"):
                fail(f"sitemap child is not XML: {u}")
            if urlparse(u).netloc != HOST:
                fail(f"sitemap child host is not {HOST}: {u}")
            sitemap_files.append(path)
except Exception as exc:
    fail(f"sitemap.xml parse error: {exc}")

if len(sitemap_urls) != len(set(sitemap_urls)):
    fail("duplicate child sitemap URL detected")

all_urls = set()
for name in sitemap_files:
    p = Path(name)
    if not p.exists():
        fail(f"missing child sitemap file: {name}")
        continue
    try:
        root = ET.parse(p).getroot()
        if root.tag != f"{{{NS['sm']}}}urlset":
            fail(f"{name} is not a urlset")
        for loc in root.findall("sm:url/sm:loc", NS):
            if loc.text:
                u = loc.text.strip()
                if urlparse(u).netloc != HOST:
                    fail(f"{name}: wrong host: {u}")
                if u in all_urls:
                    warnings.append(f"duplicate URL across sitemaps: {u}")
                all_urls.add(u)
    except Exception as exc:
        fail(f"{name} parse error: {exc}")

missing = [u for u in REQUIRED if "https://" + HOST + u not in all_urls]
for u in missing:
    fail(f"required architecture URL missing from sitemap set: {u}")

for path in ["robots.txt", "llms.txt"]:
    if not Path(path).is_file() or not Path(path).read_text(encoding="utf-8", errors="ignore").strip():
        fail(f"required file missing or empty: {path}")

robots = Path("robots.txt").read_text(encoding="utf-8", errors="ignore") if Path("robots.txt").exists() else ""
if "Sitemap: https://" + HOST + "/sitemap.xml" not in robots:
    fail("robots.txt does not reference the primary sitemap")

llms = Path("llms.txt").read_text(encoding="utf-8", errors="ignore") if Path("llms.txt").exists() else ""
for token in ["/products/rebar/", "/products/beam/", "/products/profile/", "/products/channel/", "/prices/", "/buy-iron/"]:
    if token not in llms:
        fail(f"llms.txt missing core route: {token}")
if "سلسله مراتب منبع" not in llms and "سلسله مراتب منبع" not in llms.replace("سلسله", "سلسله"):
    # Persian source hierarchy wording can vary; the explicit section below is the stable signal.
    if "سلسله مراتب منبع" not in llms and "قواعد پاسخ دقیق" not in llms:
        warnings.append("llms.txt source hierarchy heading not detected exactly")

ai_map = Path("reference/ai-retrieval-map/index.html")
if not ai_map.exists():
    fail("AI retrieval map is missing")
else:
    html = ai_map.read_text(encoding="utf-8", errors="ignore")
    if 'rel="canonical"' not in html or "https://" + HOST + "/reference/ai-retrieval-map/" not in html:
        fail("AI retrieval map canonical is missing or not normalized")
    if "dateModified" not in html:
        fail("AI retrieval map dateModified is missing")
    if 'https://' + HOST + '/reference/ai-retrieval-map/' not in all_urls:
        fail("AI retrieval map is not present in sitemap set")

for p in Path(".").rglob("*.html"):
    if ".git" in p.parts:
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    if re.search(r'https?://(www\.)?ahaneiffel\.com', text, re.I):
        fail(f"{p}: alternate domain reference detected")
    if re.search(r'href=["\']http://ahaneiffel\.top/', text, re.I):
        warnings.append(f"{p}: HTTP internal URL detected")

report = {
    "host": HOST,
    "child_sitemaps": len(sitemap_urls),
    "indexed_sitemap_urls": len(all_urls),
    "required_routes": len(REQUIRED),
    "missing_required_routes": missing,
    "warnings": warnings,
    "errors": errors,
    "status": "PASS" if not errors else "FAIL",
}
Path("seo-architecture-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors:
    sys.exit(1)
