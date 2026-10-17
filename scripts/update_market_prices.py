#!/usr/bin/env python3
"""Render family-level base prices into existing Ahaneiffel HTML price tables.

The JSON feed is authoritative. Family-only rows display the family price;
size-specific rows display it as a base price ("از ..."). No size-specific
price is inferred from a family-level price.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

DATA = Path("data/market-prices.json")
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
FAMILIES = {
    "میلگرد": ("میلگرد", "میلگرد آجدار", "میلگرد فولادی"),
    "تیرآهن": ("تیرآهن", "تیرآهن فولادی", "تیرآهن ipe", "تیرآهن IPE"),
    "پروفیل": ("پروفیل", "قوطی پروفیل", "قوطی"),
    "نبشی": ("نبشی", "نبشی فولادی"),
    "ناودانی": ("ناودانی", "ناودانی آهنی"),
    "ورق سیاه": ("ورق سیاه", "ورق فولادی سیاه", "ورق سیاه صنعتی"),
    "ورق شیروانی": ("ورق شیروانی", "ورق رنگی شیروانی"),
    "لوله": ("لوله", "لوله فولادی", "لوله داربستی"),
    "پلیت": ("پلیت", "صفحه پلیت"),
    "ورق پانچ": ("ورق پانچ", "ورق سوراخ دار"),
}

def norm(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", value)).translate(DIGITS).lower()
    value = value.replace("×", "x").replace("✕", "x").replace("٬", "").replace(",", "")
    return re.sub(r"\s+", " ", value).strip()

def format_price(value):
    return f"{int(round(float(value))):,}".replace(",", "٬").translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def load_prices():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    prices = {}
    for row in payload.get("rows", []):
        raw = row.get("raw", [])
        label = norm(" ".join(str(x) for x in raw))
        price = row.get("price")
        if price is None:
            continue
        for family, aliases in FAMILIES.items():
            if any(norm(alias) == label or norm(alias) in label for alias in aliases):
                # Prefer the canonical/most specific row for each family.
                if family not in prices or norm(family) == label:
                    prices[family] = price
    if not prices:
        raise RuntimeError(f"No usable family prices found in {DATA}")
    return payload, prices

def family_for(text):
    n = norm(text)
    # Specific labels are checked before generic "ورق".
    for family, aliases in sorted(FAMILIES.items(), key=lambda item: max(map(len, item[1])), reverse=True):
        if any(norm(alias) in n for alias in aliases):
            return family
    return None

def family_only(product, family):
    n = norm(product)
    return n in {norm(family), *(norm(alias) for alias in FAMILIES[family])}

def render_file(path, payload, prices, dry_run, report):
    original = path.read_text(encoding="utf-8", errors="replace")
    changed = original
    table_count = 0
    rows_seen = 0

    def table_replacer(match):
        nonlocal table_count, rows_seen
        table = match.group(0)
        table_changed = table
        row_pattern = re.compile(r"<tr\b[^>]*>.*?</tr\s*>", re.I | re.S)
        matched_rows = []
        for row_match in list(row_pattern.finditer(table)):
            row = row_match.group(0)
            cells = list(re.finditer(r"<td\b[^>]*>.*?</td\s*>", row, re.I | re.S))
            if len(cells) < 2:
                continue
            cell_texts = [html.unescape(re.sub(r"<[^>]+>", " ", c.group(0))).strip() for c in cells]
            # Product labels are typically in the first cell; search the first
            # two cells only to avoid mistaking a price/description for a product.
            product = " ".join(cell_texts[:2])
            family = family_for(product)
            if not family or family not in prices:
                continue
            rows_seen += 1
            exact_family = any(family_only(cell_texts[i], family) for i in range(min(2, len(cell_texts))))
            price_text = format_price(prices[family]) + " تومان / کیلوگرم"
            if not exact_family:
                price_text = "از " + price_text
            last = cells[-1]
            old_inner = re.sub(r"^<td\b[^>]*>|</td\s*>$", "", last.group(0), flags=re.I | re.S).strip()
            # Do not overwrite non-price cells such as links/actions. Only render
            # when the final cell looks like a price/status cell or the table has
            # a recognizable price header.
            headers = " ".join(re.findall(r"<th\b[^>]*>(.*?)</th\s*>", table, re.I | re.S))
            price_table = bool(re.search(r"قیمت|تومان|price", headers + " " + table[:800], re.I))
            if not price_table:
                continue
            new_cell = re.sub(r"^(<td\b[^>]*>).*?(</td\s*>)$", lambda m: m.group(1) + html.escape(price_text) + m.group(2), last.group(0), flags=re.I | re.S)
            start, end = row_match.span()
            new_row = row[:last.start()] + new_cell + row[last.end():]
            table_changed = table_changed[:start] + new_row + table_changed[end:]
            matched_rows.append((product, family, exact_family, price_text))
        if matched_rows:
            table_count += 1
            for product, family, exact_family, price_text in matched_rows:
                report.append((str(path), product, "خانوادگی" if exact_family else "سایز مشخص", family, price_text))
            date_line = f'<p class="last-update" dir="rtl">آخرین به‌روزرسانی: {html.escape(str(payload.get("published_date", "نامشخص")))}</p>'
            # Replace any existing update line directly following the table.
            tail = table_changed[table_changed.lower().rfind("</table>") + 8:]
            if not re.match(r"\s*<p\b[^>]*class=[\"'][^\"']*last-update", tail, re.I):
                table_changed = re.sub(r"(</table\s*>)", r"\1" + date_line, table_changed, count=1, flags=re.I)
            else:
                table_changed = re.sub(r"(<p\b[^>]*class=[\"'][^\"']*last-update[\"'][^>]*>).*?(</p\s*>)", lambda m: m.group(1) + "آخرین به‌روزرسانی: " + html.escape(str(payload.get("published_date", "نامشخص"))) + m.group(2), table_changed, count=1, flags=re.I | re.S)
        return table_changed

    # Only process existing HTML tables; no page/table is created.
    changed = re.sub(r"<table\b[^>]*>.*?</table\s*>", table_replacer, changed, flags=re.I | re.S)
    if changed != original and not dry_run:
        path.write_text(changed, encoding="utf-8")
    return table_count, rows_seen, changed != original

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Report proposed price rendering without changing files")
    args = parser.parse_args()
    payload, prices = load_prices()
    report = []
    files = [Path("index.html")] + sorted(Path("prices").rglob("*.html")) if Path("prices").exists() else [Path("index.html")]
    files = [p for p in files if p.is_file()]
    total_tables = total_rows = changed_files = 0
    for path in files:
        tables, rows, changed = render_file(path, payload, prices, args.dry_run, report)
        total_tables += tables
        total_rows += rows
        changed_files += int(changed)
    print("| page | product | size | matched source row | rendered price |")
    print("|---|---|---|---|---|")
    for page, product, size, family, price in report:
        print(f"| {page} | {product.replace('|', '/')} | {size} | {family} ({format_price(prices[family])}) | {price} |")
    print(f"Tables with family price rows: {total_tables}; rows inspected/matched: {total_rows}; files {'that would change' if args.dry_run else 'changed'}: {changed_files}; dry-run: {args.dry_run}")
    if args.dry_run:
        print("Dry-run only: no files changed.")

if __name__ == "__main__":
    main()
