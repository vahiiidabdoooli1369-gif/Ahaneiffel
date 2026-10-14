#!/usr/bin/env python3
import json
from io import StringIO
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

SOURCE_URL = "https://ahaneiffel.com/page/927/قیمت-روز-آهن-آلات-میلگرد-تیرآهن-نبشی-پروفیل/"
OUT = Path("data/market-prices.json")
# Daily prices supplied by the site owner are authoritative; never overwrite them with scraped/adjusted values.
if OUT.exists():
    try:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        if existing.get("source_type") == "manual-user-provided":
            print("Keeping manually supplied Ahaneiffel daily prices unchanged")
            raise SystemExit(0)
    except (json.JSONDecodeError, OSError):
        pass
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

response = requests.get(SOURCE_URL, timeout=30, headers={"User-Agent": "Ahaneiffel-PriceFeed/1.0"})
response.raise_for_status()
tables = pd.read_html(StringIO(response.text))
rows = []
for table in tables:
    table = table.fillna("")
    for _, row in table.iterrows():
        values = [clean(v) for v in row.tolist()]
        price = next((price_value(v) for v in reversed(values) if price_value(v) and price_value(v) >= MIN_PRICE), None)
        if price is not None:
            rows.append({"raw": values, "source_price": price, "price": max(MIN_PRICE, price + PRICE_OFFSET)})
if not rows:
    raise RuntimeError("No price rows extracted from authorized Ahaneiffel.com price page")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    "source": SOURCE_URL,
    "source_type": "Ahaneiffel.com price page",
    "price_adjustment_toman_per_unit": PRICE_OFFSET,
    "price_adjustment_note": "قیمت منبع بدون تعدیل خودکار ثبت شده است؛ پیش از انتشار یا سفارش باید توسط کارشناس تایید شود.",
    "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    "rows": rows
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Extracted {len(rows)} price rows")
