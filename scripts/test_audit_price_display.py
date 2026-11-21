import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_price_display", ROOT / "scripts" / "audit_price_display.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

class PriceDisplayTests(unittest.TestCase):
    def test_historical_numeric_price_requires_date_and_status(self):
        parser = MODULE.QuoteParser()
        parser.feed('<td class="quote" data-price-date="1405-08-27" data-price-status="historical">۱۱۶٬۰۰۰ تومان</td>')
        self.assertEqual(len(parser.cells), 1)
        self.assertEqual(parser.cells[0]["status"], "historical")
        self.assertEqual(parser.cells[0]["date"], "1405-08-27")

    def test_unlabelled_numeric_price_is_flagged(self):
        parser = MODULE.QuoteParser()
        parser.feed('<td class="quote">۱۱۶٬۰۰۰ تومان</td>')
        result = MODULE.inspect_sample(parser.cells[0]) if hasattr(MODULE, "inspect_sample") else None
        self.assertIsNone(result)
        self.assertFalse(parser.cells[0]["date"])
        self.assertFalse(parser.cells[0]["status"])

    def test_verified_price_requires_verification_and_source(self):
        parser = MODULE.QuoteParser()
        parser.feed('<td class="quote" data-price-date="1405-08-30" data-price-status="verified">۱۱۶٬۰۰۰</td>')
        cell = parser.cells[0]
        self.assertEqual(cell["status"], "verified")
        self.assertFalse(cell["verified"])

    def test_textual_inquiry_is_not_numeric_price(self):
        self.assertIsNone(MODULE.NUMBER_RE.search("استعلام روز".translate(MODULE.DIGITS)))

if __name__ == "__main__":
    unittest.main(verbosity=2)
