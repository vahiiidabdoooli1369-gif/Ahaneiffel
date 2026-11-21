#!/usr/bin/env python3
"""Small regression tests for the page-date audit."""
import importlib.util
from datetime import date, datetime, timezone
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("audit_page_dates",ROOT/"scripts"/"audit_page_dates.py")
MODULE=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

class PageDateAuditTests(unittest.TestCase):
    def test_jalali_conversion(self):
        self.assertEqual(MODULE.gregorian_to_jalali(date(2026,11,19)),"1405/08/28")
    def test_tehran_calendar_date_at_utc_day_boundary(self):
        utc_time = datetime(2026, 11, 20, 21, 0, tzinfo=timezone.utc)
        self.assertEqual(MODULE.tehran_today(utc_time), date(2026, 11, 21))

    def test_visible_date_with_persian_digits(self):
        html="<p>آخرین بازبینی محتوای این صفحه: ۱۴۰۵/۰۸/۲۸</p>"
        self.assertEqual(len(list(MODULE.VISIBLE_RE.finditer(html))),1)
    def test_structured_dates_are_detected(self):
        html='<meta name="dateModified" content="2026-11-19"><script>{"dateModified":"2026-11-19"}</script>'
        self.assertEqual(MODULE.ISO_RE.findall(html),["2026-11-19"])
        self.assertEqual(MODULE.META_RE.findall(html),["2026-11-19"])

if __name__=="__main__":
    unittest.main(verbosity=2)
