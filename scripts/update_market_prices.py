#!/usr/bin/env python3
import argparse
import html
import json
import re
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

parser = argparse.ArgumentParser(description="Render verified market prices into static HTML")
parser.add_argument("--dry-run", action="store_true", help="Print exact family+size matches without changing files")
args = parser.parse_args()

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

FAMILY_TERMS = {
    "میلگرد": ("میلگرد", "rebar"),
    "تیرآهن": ("تیرآهن", "تيرآهن", "beam", "ipe"),
    "پروفیل": ("پروفیل", "قوطی", "profile"),
    "نبشی": ("نبشی", "angle"),
    "ناودانی": ("ناودانی", "channel"),
    "ورق": ("ورق", "sheet", "plate"),
}

def family_key(value):
    text = clean(value).lower()
    for family, terms in FAMILY_TERMS.items():
        if any(term.lower() in text for term in terms):
            # Avoid treating specialized sheet types as generic sheet only
            # when the source row explicitly says ورق; both still map to ورق.
            return family
    return None

def size_keys(value):
    text = clean(value).lower().replace("×", "x").replace("*", "x").replace("٫", ".")
    found = []
    # Dimensions such as 60x40 are one exact size; standalone sizes such as 14
    # are exact too. Avoid extracting arbitrary numbers from prices/weights.
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?(?:\s*x\s*\d+(?:\.\d+)?)?)(?![\w.])", text):
        token = re.sub(r"\s+", "", m.group(1))
        if token not in found:
            found.append(token)
    return found

def source_match(page_family, page_sizes, row):
    raw = row.get("raw", [])
    # The price is a separate field in the feed and must never count as size.
    descriptive_values = raw[:-1] if row.get("source_price") is not None and len(raw) > 1 else raw
    descriptive = " ".join(map(str, descriptive_values))
    if family_key(descriptive) != page_family:
        return False
    source_sizes = set()
    for value in descriptive_values:
        # Only numbers in source values that look like product sizes can match.
        source_sizes.update(size_keys(value))
    return bool(set(page_sizes) & source_sizes)

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
    if not args.dry_run:
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {len(rows)} price rows")

rows = data.get("rows", [])
if not rows:
    raise RuntimeError("market-prices.json has no rows; cannot render static prices")

def update_table(html_text, page_path, dry_run_rows):
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
        cell_texts = [plain(cell.group(2)) for cell in cells]
        combined = " ".join(cell_texts)
        family = family_key(combined)
        target = next((cell for cell in cells if re.search(r"\bquote\b", cell.group(1), re.I)), None)
        if target is None and len(cells) >= 3:
            target = cells[-2] if len(cells) >= 4 else cells[2]
        # Ignore the price/status cell and non-size measurements. Only exact
        # size-shaped cells are considered, never a shared number in prose.
        descriptive_cells = [txt for cell, txt in zip(cells, cell_texts) if cell is not target]
        page_sizes = []
        for txt in descriptive_cells:
            compact = clean(txt).replace("×", "x").replace("*", "x")
            if re.fullmatch(r"\d+(?:\.\d+)?(?:\s*x\s*\d+(?:\.\d+)?)?(?:\s*(?:mm|میل))?", compact, re.I):
                page_sizes.extend(size_keys(compact))
            else:
                # Product links may include the size in their label (e.g. میلگرد 14).
                for size in size_keys(compact):
                    if re.search(r"(?:میلگرد|تیرآهن|پروفیل|قوطی|نبشی|ناودانی|ورق|rebar|beam|profile|angle|channel|sheet)", compact, re.I):
                        page_sizes.append(size)
        page_sizes = list(dict.fromkeys(page_sizes))
        matches = [item for item in rows if family and page_sizes and source_match(family, page_sizes, item)]
        best = matches[0] if len(matches) == 1 else None
        product = next((txt for txt in cell_texts if family_key(txt) == family), family or "نامشخص")
        size_label = ", ".join(page_sizes) if page_sizes else "نامشخص"
        source_label = " | ".join(map(str, best.get("raw", []))) if best else "بدون تطبیق دقیق"
        amount_label = f'{int(round(float(best["price"]))):,} تومان' if best else "بدون تغییر"
        dry_run_rows.append((page_path, product, size_label, source_label, amount_label))
        if not best or target is None:
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
dry_run_rows = []
html_paths = [Path("index.html")]
prices_dir = Path("prices")
if prices_dir.exists():
    html_paths.extend(sorted(prices_dir.rglob("index.html")))

for path in html_paths:
    if not path.is_file():
        continue
    before = path.read_text(encoding="utf-8")
    after = update_table(before, path.as_posix(), dry_run_rows)
    if after != before and not args.dry_run:
        path.write_text(after, encoding="utf-8")
        changed_pages.add(path.as_posix())
        print(f"Rendered static prices: {path.as_posix()}")

if args.dry_run:
    print("| page | product | size | matched source row | price |")
    print("|---|---|---|---|---|")
    for page, product, size, source_row, price in dry_run_rows:
        print(f"| {page} | {product} | {size} | {source_row} | {price} |")
    print(f"Rows inspected: {len(dry_run_rows)}; exact matches: {sum(1 for row in dry_run_rows if row[4] != 'بدون تغییر')} (dry-run: no files changed)")

# Update only sitemap entries whose corresponding price-page HTML changed.
if changed_pages and SITEMAP.exists() and not args.dry_run:
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
