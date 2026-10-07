from pathlib import Path
import re
import sys
from html import unescape
from urllib.parse import urlparse
import json

errors = []
warnings = []
checked = 0
skipped = 0
RULES_PER_DOCUMENT = 25
ALLOWED_HOSTS = {"ahaneiffel.top", "www.ahaneiffel.top"}

def attr(tag, name):
    m = re.search(r"\b" + re.escape(name) + r"\s*=\s*[\"']([^\"']*)[\"']", tag, re.I)
    return unescape(m.group(1).strip()) if m else ""

def count(pattern, text):
    return len(re.findall(pattern, text, re.I | re.S))

for path in Path(".").rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<!doctype\s+html|<html\b", text, re.I):
        skipped += 1
        continue
    checked += 1

    if count(r"<html\b", text) != 1:
        errors.append(f"{path}: expected exactly one <html> element")
    if count(r"<head\b", text) != 1:
        errors.append(f"{path}: expected exactly one <head> element")
    if count(r"<body\b", text) != 1:
        errors.append(f"{path}: expected exactly one <body> element")
    end = re.search(r"</html\s*>", text, re.I)
    if end and text[end.end():].strip():
        errors.append(f"{path}: content exists after </html>")
    if not re.search(r"<meta\b[^>]+charset=", text, re.I):
        warnings.append(f"{path}: charset meta not detected")

    robots = re.findall(r'<meta\b[^>]+name=["\']robots["\'][^>]*>', text, re.I)
    if not robots:
        warnings.append(f"{path}: robots meta not detected")
    canonical_tags = re.findall(r'<link\b[^>]+rel=["\']canonical["\'][^>]*>', text, re.I)
    is_404 = path.name.lower() == "404.html"
    if is_404:
        # GitHub Pages 404 documents are error handlers, not indexable documents.
        # A canonical is neither required nor desirable here.
        canonical = attr(canonical_tags[0], "href") if canonical_tags else ""
    else:
        if len(canonical_tags) != 1:
            errors.append(f"{path}: expected exactly one canonical link")
        canonical = attr(canonical_tags[0], "href") if canonical_tags else ""
    if canonical and "index.html" in canonical:
        # Directory index documents are served at the clean directory URL.
        # Accept the equivalent /path/index.html form when the file itself is
        # the directory's index document; this prevents false failures on
        # statically generated GitHub Pages URLs.
        expected_file = "https://ahaneiffel.top/" + str(path).replace("\\", "/").lstrip("./")
        if not (str(path).endswith("/index.html") and canonical.rstrip("/") == expected_file.rstrip("/")):
            errors.append(f"{path}: canonical contains unexpected index.html: {canonical}")
    if canonical and urlparse(canonical).scheme in {"http", "https"} and urlparse(canonical).netloc not in ALLOWED_HOSTS:
        errors.append(f"{path}: canonical host outside Ahaneiffel: {canonical}")
    if canonical and not canonical.startswith("https://ahaneiffel.top/"):
        warnings.append(f"{path}: canonical is not normalized to non-www HTTPS: {canonical}")
    if re.search(r'<meta\b[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        warnings.append(f"{path}: noindex page detected")

    titles = re.findall(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    if len(titles) != 1:
        errors.append(f"{path}: expected exactly one title")
    elif not unescape(re.sub(r"\s+", " ", titles[0])).strip():
        errors.append(f"{path}: title is empty")
    descriptions = re.findall(r'<meta\b[^>]+name=["\']description["\'][^>]*>', text, re.I)
    if len(descriptions) != 1:
        warnings.append(f"{path}: expected one meta description")
    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    if len(h1s) != 1:
        warnings.append(f"{path}: expected one visible H1")
    html_open = re.search(r"<html\b[^>]*>", text, re.I)
    if html_open and not attr(html_open.group(0), "lang"):
        warnings.append(f"{path}: html lang attribute missing")
    if not re.search(r'<meta\b[^>]+name=["\']viewport["\']', text, re.I):
        warnings.append(f"{path}: viewport meta not detected")

    jsonld = re.findall(r'<script\b[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S)
    for block in jsonld:
        if "index.html" in block and not (
            str(path).endswith("/index.html")
            and "https://ahaneiffel.top/" + str(path.parent).replace("\\", "/").strip("./") + "/index.html" in block
        ):
            errors.append(f"{path}: JSON-LD contains unexpected index.html URL")
        try:
            data = json.loads(block)
            if not isinstance(data, (dict, list)):
                errors.append(f"{path}: JSON-LD root must be object or array")
        except Exception as exc:
            errors.append(f"{path}: invalid JSON-LD: {exc}")
    if jsonld and not re.search(r'"@context"\s*:\s*"https://schema\.org"', jsonld[0]):
        warnings.append(f"{path}: JSON-LD context is not schema.org")
    if re.search(r'<meta\b[^>]+property=["\']og:title["\']', text, re.I) and not re.search(r'<meta\b[^>]+property=["\']og:description["\']', text, re.I):
        warnings.append(f"{path}: og:title without og:description")
    if re.search(r'<meta\b[^>]+property=["\']og:url["\']', text, re.I) and not re.search(r'<meta\b[^>]+property=["\']og:type["\']', text, re.I):
        warnings.append(f"{path}: og:url without og:type")
    if re.search(r'<meta\b[^>]+property=["\']og:image["\']', text, re.I) and "favicon.svg" in text:
        warnings.append(f"{path}: og:image uses favicon.svg")

    for tag in re.findall(r"<a\b[^>]*>", text, re.I):
        href = attr(tag, "href")
        if href.startswith("http://ahaneiffel.top/"):
            warnings.append(f"{path}: internal HTTP link: {href}")
    for img in re.findall(r"<img\b[^>]*>", text, re.I):
        if not attr(img, "alt"):
            warnings.append(f"{path}: image missing alt")
    if re.search(r'<script\b[^>]+src=["\']http://', text, re.I):
        errors.append(f"{path}: insecure HTTP script source")
    if count(r'<meta\b[^>]+http-equiv=["\']refresh["\']', text) > 0:
        warnings.append(f"{path}: meta refresh detected")
    if count(r"<iframe\b", text) > 0:
        warnings.append(f"{path}: iframe detected")

print(f"HTML quality audit: {checked} standalone documents × {RULES_PER_DOCUMENT} rules = {checked * RULES_PER_DOCUMENT} checks; {skipped} fragments skipped")
for w in warnings[:300]:
    print("WARN", w)
for e in errors[:300]:
    print("ERROR", e)
if errors:
    sys.exit(1)
print("PASS: no blocking HTML/SEO integrity errors detected.")
