from pathlib import Path
import json
import re
import sys
from html import unescape
from urllib.parse import urlparse

errors = []
checked = 0
skipped = 0
ALLOWED_HOSTS = {"ahaneiffel.top", "www.ahaneiffel.top"}

def attr(tag, name):
    match = re.search(r"\b" + re.escape(name) + r"""\\s*=\\s*["']([^"']*)["']""", tag, re.I)
    return unescape(match.group(1).strip()) if match else ""

for path in Path(".").rglob("*.html"):
    if ".git" in path.parts or "node_modules" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"<!doctype\s+html|<html\b", text, re.I):
        skipped += 1
        continue

    robots_tags = re.findall(r"<meta\b[^>]*>", text, re.I)
    is_noindex = any(
        attr(tag, "name").lower() == "robots"
        and "noindex" in attr(tag, "content").lower()
        for tag in robots_tags
    )
    if is_noindex or path.name.lower() == "404.html":
        skipped += 1
        continue

    checked += 1
    link_tags = re.findall(r"<link\b[^>]*>", text, re.I)
    canonical_tags = [
        tag for tag in link_tags
        if "canonical" in attr(tag, "rel").lower().split()
    ]
    if len(canonical_tags) != 1:
        errors.append(f"{path}: expected exactly one canonical link")
    for tag in canonical_tags:
        canonical = attr(tag, "href")
        if not canonical:
            errors.append(f"{path}: canonical href is empty")
            continue
        parsed = urlparse(canonical)
        if parsed.scheme in {"http", "https"} and parsed.netloc not in ALLOWED_HOSTS:
            errors.append(f"{path}: unexpected canonical host: {canonical}")
        if "index.html" in parsed.path and not str(path).endswith("/index.html"):
            errors.append(f"{path}: canonical contains unexpected index.html: {canonical}")

    jsonld_blocks = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>',
        text, re.I | re.S
    )
    for block in jsonld_blocks:
        try:
            data = json.loads(unescape(block).strip())
            if not isinstance(data, (dict, list)):
                errors.append(f"{path}: JSON-LD root must be an object or array")
        except (json.JSONDecodeError, TypeError) as exc:
            errors.append(f"{path}: invalid JSON-LD: {exc}")

print(
    f"SEO structured-data integrity: {checked} indexable HTML documents checked; "
    f"{skipped} fragments/noindex/404 documents skipped"
)
for error in errors[:300]:
    print("ERROR", error)
if errors:
    sys.exit(1)
print("PASS: canonical and JSON-LD integrity checks passed.")
