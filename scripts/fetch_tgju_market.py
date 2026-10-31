#!/usr/bin/env python3
"""Read-only TGJU public-page importer. Never changes Ahaneiffel product prices."""
import json, re
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AhaneiffelMarketBoard/1.0)"}
URLS = {
    "dollar": "https://www.tgju.org/profile/price_dollar_rl",
    "metals": "https://www.tgju.org/basemetal",
}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def clean(value):
    return re.sub(r"\s+", " ", str(value).translate(DIGITS)).strip()

def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=25)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text

def tables(html):
    return pd.read_html(StringIO(html))

def row_values(all_tables, label):
    for table in all_tables:
        for _, row in table.fillna("").iterrows():
            cells = [clean(v) for v in row.tolist()]
            if any(label in cell for cell in cells):
                nums = []
                for cell in cells:
                    match = re.search(r"(?<![\w])([0-9][0-9,]*(?:\.\d+)?)", cell.replace("٬", ","))
                    if match:
                        try: nums.append(float(match.group(1).replace(",", "")))
                        except ValueError: pass
                if nums:
                    return nums
    return []

def main():
    dollar_html = fetch_html(URLS["dollar"])
    metal_html = fetch_html(URLS["metals"])
    dollar_text = clean(BeautifulSoup(dollar_html, "lxml").get_text(" ", strip=True))
    current = re.search(r"نرخ فعلی\s*:?\s*([0-9][0-9,٬]*)", dollar_text)
    dollar_rial = float(current.group(1).replace(",", "").replace("٬", "")) if current else None
    aluminum_nums = row_values(tables(metal_html), "آلومینیوم")
    # TGJU quotes the domestic dollar in rial; publish toman.
    aluminum_usd_ton = next((n for n in aluminum_nums if 500 <= n <= 10000), None)
    if dollar_rial is None or aluminum_usd_ton is None:
        raise RuntimeError(f"Could not validate TGJU quotes (dollar candidates={dollar_nums}, aluminum candidates={aluminum_nums})")
    payload = {
        "source": "TGJU",
        "source_urls": URLS,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "نرخ‌های منبع ممکن است با تأخیر باشند؛ نرخ دلار از ریال به تومان تبدیل شده است. قیمت آلومینیوم جهانی بر حسب دلار به ازای هر تن متریک است. این داده‌ها قیمت قطعی فروش آهن‌آلات نیستند.",
        "items": [
            {"id":"usd_irr","name":"دلار آزاد","value":round(dollar_rial/10),"unit":"تومان","source_unit":"ریال"},
            {"id":"aluminum","name":"آلومینیوم جهانی","value":aluminum_usd_ton,"unit":"دلار / تن"}
        ]
    }
    out = Path("data/tgju-market.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Updated TGJU market board")

if __name__ == "__main__":
    main()
