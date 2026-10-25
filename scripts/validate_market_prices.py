#!/usr/bin/env python3
"""Validate the public market-price JSON contract without changing price data."""
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "data" / "market-prices.json"
ERRORS = []
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def fail(message):
    ERRORS.append(message)


def normalize_alias(value):
    value = str(value).translate(DIGITS).lower()
    value = re.sub(r"[\u200c\u200d\s\-_]+", "", value)
    return value


def validate(data):
    if not isinstance(data, dict):
        fail("feed root must be a JSON object")
        return
    for field in ("source", "source_type", "published_date", "currency", "unit", "updated_at_utc", "rows"):
        if field not in data:
            fail(f"missing required field: {field}")
    for field in ("source", "source_type", "published_date", "currency", "unit"):
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            fail(f"{field} must be a non-empty string")

    if isinstance(data.get("published_date"), str):
        normalized = data["published_date"].translate(DIGITS)
        if not re.fullmatch(r"\d{4}[/-]\d{1,2}[/-]\d{1,2}", normalized):
            fail("published_date must be a Jalali-looking YYYY/MM/DD or YYYY-MM-DD date")
        else:
            year, month, day = map(int, re.split(r"[/-]", normalized))
            if year < 1300 or not 1 <= month <= 12 or not 1 <= day <= 31:
                fail("published_date components are outside supported bounds")

    timestamp = data.get("updated_at_utc")
    if not isinstance(timestamp, str) or not timestamp.strip():
        fail("updated_at_utc must be a non-empty ISO-8601 string")
    else:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                fail("updated_at_utc must include a timezone")
        except ValueError:
            fail("updated_at_utc is not valid ISO-8601")

    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        fail("rows must be a non-empty array")
        return
    if len(rows) > 1000:
        fail(f"unexpectedly large row count: {len(rows)}")

    seen_aliases = {}
    for index, row in enumerate(rows, 1):
        prefix = f"rows[{index - 1}]"
        if not isinstance(row, dict):
            fail(f"{prefix} must be an object")
            continue
        aliases = row.get("raw")
        if not isinstance(aliases, list) or not aliases:
            fail(f"{prefix}.raw must be a non-empty alias array")
        else:
            valid_aliases = 0
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    fail(f"{prefix}.raw contains an empty/non-string alias")
                    continue
                normalized = normalize_alias(alias)
                if normalized in seen_aliases:
                    fail(f"duplicate alias {alias!r} in {prefix}; already used by {seen_aliases[normalized]}")
                else:
                    seen_aliases[normalized] = prefix
                valid_aliases += 1
            if valid_aliases == 0:
                fail(f"{prefix} has no usable aliases")

        price = row.get("price")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            fail(f"{prefix}.price must be a finite positive number")

        if "unit" in row and (not isinstance(row["unit"], str) or not row["unit"].strip()):
            fail(f"{prefix}.unit must be a non-empty string when supplied")

    if data.get("source_type") == "manual-user-provided" and not data.get("price_adjustment_note"):
        fail("manual-user-provided feed should explain price confirmation/adjustment policy")


def main():
    try:
        data = json.loads(FEED.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FEED_INVALID: cannot read JSON feed: {exc}")
        return 1
    validate(data)
    if ERRORS:
        print("MARKET_PRICE_FEED_INVALID")
        for issue in ERRORS:
            print(f"- {issue}")
        return 1
    print(f"MARKET_PRICE_FEED_VALID: {len(data['rows'])} rows; schema, dates, timestamps, prices, and aliases checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
