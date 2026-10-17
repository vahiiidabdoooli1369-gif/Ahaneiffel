#!/usr/bin/env python3
import html
import json
import re
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

SOURCE_URL = "https://ahaneiffel.com/page/927/قیمت-روز-آهن-آلات-میلگرد-تیرآهن-نبشی-پروفیل/"
OUT = Path("data/market-prices.json")
SITEMAP = Path("sitemap-prices.xml")
PRICE_START = "<!-- prices:start -->"
PRICE_END = "<!-- prices:end -->"
MIN_PRICE = 1000
PRICE_OFFSET = 0
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def clean(value):
    s = str(value).translate(DIGITS)
    s = s.replace(",", "").replace("٬", "").replace("٫", ".")
    return re.sub(r"\s+", " ", s).strip()

def price_value(value):
    s = clean(value)
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def text(self):
        return clean(" ".join(self.parts))

def plain(markup):
    parser = TextOnly()
    parser.feed(markup)
    return parser.text()

def tokens(value):
    return re.findall(r"[a-zآ-ی]+|\d+(?:\.\d+)?", clean(value).lower())

def match_score(left, right):
    right_tokens = set(tokens(right))
    return sum(4 if token[0].isdigit() else 2 for token in tokens(left) if token in right_tokens)

def fetch_rows():
    response = requests.get(SOURCE_URL, timeout=30, headers={"User-Agent": "Ahaneiffel-PriceFeed/1.0"})
    response.raise_for_status()
    rows = []
    for table in pd.read_html(StringIO(response.text)):
        table = table.fillna("")
        for _, row in table.iterrows():
            values = [clean(v) for v in row.tolist()]
            price = next((price_value(v) for v in reversed(values) if price_value(v) and price_value(v) >= MIN_PRICE), None)
            if price is not None:
                rows.append({"raw": values, "source_price": price, "price": max(MIN_PRICE, price + PRICE_OFFSET)})
    if not rows:
        raise RuntimeError("No price rows extracted from authorized Ahaneiffel.com price page")
    return rows

OUT.parent.mkdir(parents=True, exist_ok=True)
existing = {}
if OUT.exists():
    try:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        existing = {}

if existing.get("source_type") == "manual-user-provided" and isinstance(existing.get("rows"), list):
    data = existing
    print("Keeping manually supplied Ahaneiffel prices; rendering their existing values into HTML")
else:
    rows = fetch_rows()
    data = {
        "source": SOURCE_URL,
        "source_type": "Ahaneiffel.com price page",
        "price_adjustment_toman_per_unit": PRICE_OFFSET,
        "price_adjustment_note": "قیمت منبع بدون تعدیل خودکار ثبت شده است؛ پیش از انتشار یا سفارش باید توسط کارشناس تایید شود.",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {len(rows)} price rows")

rows = data.get("rows", [])
if not rows:
    raise RuntimeError("market-prices.json has no rows; cannot render static prices")

def update_table(html_text):
    # Remove previous generated markers before recomputing the static table.
    html_text = html_text.replace(PRICE_START, "").replace(PRICE_END, "")
    table_pattern = re.compile(r"<table\b(?=[^>]*class=[\"'][^\"']*\bprice-table\b[^\"']*[\"'])[^>]*>[\s\S]*?</table>", re.I)
    table_match = table_pattern.search(html_text)
    if not table_match:
        return html_text
    table = table_match.group(0)
    tbody_pattern = re.compile(r"(<tbody\b[^>]*>)([\s\S]*?)(</tbody>)", re.I)
    tbody_match = tbody_pattern.search(table)
    if not tbody_match:
        return html_text
    body = tbody_match.group(2)
    changed_body = body
    row_pattern = re.compile(r"<tr\b[^>]*>[\s\S]*?</tr>", re.I)
    def update_row(row_match):
        row = row_match.group(0)
        cells = list(re.finditer(r"<td\b([^>]*)>([\s\S]*?)</td>", row, re.I))
        if not cells:
            return row
        row_text = " ".join(plain(cell.group(2)) for cell in cells)
        best = max(rows, key=lambda item: match_score(row_text, " ".join(map(str, item.get("raw", [])))), default=None)
        score = match_score(row_text, " ".join(map(str, best.get("raw", [])))) if best else 0
        if not best or score < 4:
            return row
        target = next((cell for cell in cells if re.search(r"\bquote\b", cell.group(1), re.I)), None)
        if target is None and len(cells) >= 3:
            target = cells[2]
        if target is None:
            return row
        amount = f'{int(round(float(best["price"]))):,}'
        replacement = target.group(0)[:target.start(2)-target.start()] + amount + " تومان" + target.group(0)[target.end(2)-target.start():]
        start, end = target.start(), target.end()
        return row[:start] + replacement + row[end:]
    changed_body = row_pattern.sub(update_row, body)
    # Mark the static table body so subsequent runs replace rather than append.
    wrapped = "\n" + PRICE_START + "\n" + changed_body + "\n" + PRICE_END + "\n"
    new_table = table[:tbody_match.start(2)] + wrapped + table[tbody_match.end(2):]
    return html_text[:table_match.start()] + new_table + html_text[table_match.end():]

today = date.today().isoformat()
changed_pages = set()
html_paths = [Path("index.html")]
prices_dir = Path("prices")
if prices_dir.exists():
    html_paths.extend(sorted(prices_dir.rglob("index.html")))

for path in html_paths:
    if not path.is_file():
        continue
    before = path.read_text(encoding="utf-8")
    after = update_table(before)
    if after != before:
        path.write_text(after, encoding="utf-8")
        changed_pages.add(path.as_posix())
        print(f"Rendered static prices: {path.as_posix()}")

# Update only sitemap entries whose corresponding price-page HTML changed.
if changed_pages and SITEMAP.exists():
    sitemap_text = SITEMAP.read_text(encoding="utf-8")
    def update_url(match):
        block = match.group(0)
        loc_match = re.search(r"<loc>(.*?)</loc>", block, re.I)
        if not loc_match:
            return block
        url_path = re.sub(r"^https?://[^/]+", "", html.unescape(loc_match.group(1)))
        if not url_path.endswith("/"):
            url_path += "/"
        relative = url_path.removeprefix("/prices/").strip("/")
        changed_path = "prices/" + (relative + "/" if relative else "") + "index.html"
        if changed_path not in changed_pages:
            return block
        if re.search(r"<lastmod>.*?</lastmod>", block, re.I):
            return re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{today}</lastmod>", block, count=1, flags=re.I)
        return re.sub(r"(</loc>)", rf"\1<lastmod>{today}</lastmod>", block, count=1, flags=re.I)
    updated_sitemap = re.sub(r"<url\b[^>]*>[\s\S]*?</url>", update_url, sitemap_text, flags=re.I)
    if updated_sitemap != sitemap_text:
        SITEMAP.write_text(updated_sitemap, encoding="utf-8")
        print(f"Updated sitemap-prices.xml lastmod={today} for changed price pages")
