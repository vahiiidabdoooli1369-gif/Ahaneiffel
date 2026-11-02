#!/usr/bin/env python3
"""Import a broad set of public TGJU market quotes into the Ahaneiffel ticker."""
import json, re
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO
import pandas as pd
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AhaneiffelMarketBoard/2.0)"}
URLS = {
    "home": "https://www.tgju.org/",
    "local_markets": "https://www.tgju.org/local-markets",
    "metals": "https://www.tgju.org/basemetal",
}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# TGJU domestic cash quotes are normally published in rial; convert to toman.
DOMESTIC = [
    ("usd_irr", "دلار آزاد", ["دلار"], "تومان"),
    ("eur_irr", "یورو", ["یورو"], "تومان"),
    ("aed_irr", "درهم امارات", ["درهم امارات"], "تومان"),
    ("gbp_irr", "پوند انگلیس", ["پوند انگلیس"], "تومان"),
    ("try_irr", "لیر ترکیه", ["لیر ترکیه"], "تومان"),
    ("chf_irr", "فرانک سوئیس", ["فرانک سوئیس"], "تومان"),
    ("cny_irr", "یوان چین", ["یوان چین"], "تومان"),
    ("kwd_irr", "دینار کویت", ["دینار کویت"], "تومان"),
    ("sar_irr", "ریال عربستان", ["ریال عربستان"], "تومان"),
    ("rub_irr", "روبل روسیه", ["روبل روسیه"], "تومان"),
    ("gold18", "طلای ۱۸ عیار", ["طلای 18 عیار", "طلای ۱۸ عیار"], "تومان / گرم"),
    ("gold24", "طلای ۲۴ عیار", ["طلای ۲۴ عیار", "طلای 24 عیار"], "تومان / گرم"),
    ("gold_used", "طلای دست دوم", ["طلای دست دوم"], "تومان / گرم"),
    ("gold_mithqal", "مثقال طلا", ["مثقال طلا"], "تومان"),
    ("coin_emami", "سکه امامی", ["سکه امامی"], "تومان"),
    ("coin_bahar", "سکه بهار آزادی", ["سکه بهار آزادی"], "تومان"),
    ("coin_half", "نیم سکه", ["نیم سکه"], "تومان"),
    ("coin_quarter", "ربع سکه", ["ربع سکه"], "تومان"),
    ("silver_gram", "گرم نقره ۹۹۹", ["گرم نقره 999", "گرم نقره ۹۹۹"], "تومان / گرم"),
    ("tether", "تتر", ["تتر"], "تومان"),
]
GLOBAL = [
    ("gold_ounce", "انس طلا", ["انس طلا"], "دلار / اونس"),
    ("silver_ounce", "انس نقره", ["انس نقره"], "دلار / اونس"),
    ("platinum", "انس پلاتین", ["انس پلاتین"], "دلار / اونس"),
    ("palladium", "انس پالادیوم", ["انس پالادیوم"], "دلار / اونس"),
    ("bitcoin", "بیت کوین", ["بیت کوین"], "دلار"),
    ("ethereum", "اتریوم", ["اتریوم"], "دلار"),
    ("ripple", "ریپل", ["ریپل"], "دلار"),
    ("bnb", "بایننس کوین", ["بایننس کوین"], "دلار"),
    ("tron", "ترون", ["ترون"], "دلار"),
    ("stellar", "استلار", ["استلار"], "دلار"),
    ("bitcoin_cash", "بیت کوین کش", ["بیت کوین کش"], "دلار"),
]

def clean(value):
    return re.sub(r"\\s+", " ", str(value).translate(DIGITS)).replace("٬", ",").strip()

def number(value):
    text = clean(value).replace(",", "").replace("٫", ".")
    match = re.search(r"(?<![\\w])([0-9]+(?:\\.[0-9]+)?)", text)
    return float(match.group(1)) if match else None

def fetch_tables(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return pd.read_html(StringIO(response.text))

def collect_rows(all_tables):
    rows = []
    for table in all_tables:
        for _, row in table.fillna("").iterrows():
            cells = [clean(v) for v in row.tolist()]
            if len(cells) < 2:
                continue
            rows.append((cells[0], cells[1], cells))
    return rows

def find_quote(rows, aliases):
    aliases = [clean(a).replace(" ", "") for a in aliases]
    for label, price_cell, cells in rows:
        normalized = label.replace(" ", "")
        if any(normalized == a or normalized.startswith(a) for a in aliases):
            value = number(price_cell)
            if value is None:
                for cell in cells[1:]:
                    value = number(cell)
                    if value is not None:
                        break
            if value is not None and value > 0:
                return value
    return None

def main():
    rows = []
    for key in ("home", "local_markets", "metals"):
        try:
            rows.extend(collect_rows(fetch_tables(URLS[key])))
        except Exception as exc:
            print(f"Warning: could not read {key}: {exc}")

    items = []
    missing = []
    for item_id, name, aliases, unit in DOMESTIC:
        value = find_quote(rows, aliases)
        if value is None:
            missing.append(name)
            continue
        # Local currency, gold, coin and tether prices are in rial on TGJU.
        items.append({"id": item_id, "name": name, "value": round(value / 10), "unit": unit})

    for item_id, name, aliases, unit in GLOBAL:
        value = find_quote(rows, aliases)
        if value is None:
            missing.append(name)
            continue
        # Bitcoin and other crypto rows can be shown in rial on some TGJU tables.
        # Convert large rial quotes to toman; keep global USD quotes unchanged.
        if value > 10000:
            value = value / 10
            unit = "تومان"
        items.append({"id": item_id, "name": name, "value": round(value, 4), "unit": unit})

    # Industrial metals are parsed from TGJU's base-metal table.
    try:
        metal_rows = collect_rows(fetch_tables(URLS["metals"]))
        for item_id, name, aliases in [
            ("aluminum", "آلومینیوم", ["آلومینیوم"]),
            ("copper", "مس", ["مس"]),
            ("zinc", "روی", ["روی"]),
            ("lead", "سرب", ["سرب"]),
            ("nickel", "نیکل", ["نیکل"]),
            ("tin", "قلع", ["قلع"]),
        ]:
            value = find_quote(metal_rows, aliases)
            if value is not None and value > 0:
                items.append({"id": item_id, "name": name, "value": round(value, 4), "unit": "دلار / تن"})
    except Exception as exc:
        print(f"Warning: metals table unavailable: {exc}")

    # Never replace a working feed with an empty or tiny partial response.
    if len(items) < 5:
        raise RuntimeError(f"Too few valid market quotes ({len(items)}); missing={missing}")

    payload = {
        "source": "TGJU",
        "source_urls": URLS,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "قیمت‌ها از جداول عمومی TGJU گردآوری شده‌اند و ممکن است با تأخیر باشند. نرخ‌های داخلی ریالی به تومان تبدیل شده‌اند؛ برخی دارایی‌های جهانی با واحد دلار نمایش داده می‌شوند. این داده‌ها قیمت قطعی فروش آهن‌آلات نیستند.",
        "items": items,
        "missing_items": missing,
    }
    out = Path("data/tgju-market.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {len(items)} TGJU market quotes; missing: {', '.join(missing)}")

if __name__ == "__main__":
    main()
