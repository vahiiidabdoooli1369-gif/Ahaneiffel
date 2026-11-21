from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets" / "site-footer.js"

class PriceStatusNoticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ASSET.read_text(encoding="utf-8")

    def test_notice_is_scoped_to_price_routes(self):
        self.assertIn('currentPath.startsWith("/prices/")', self.source)

    def test_notice_is_accessible_and_clear(self):
        self.assertIn('setAttribute("role","note")', self.source)
        self.assertIn('setAttribute("aria-label","وضعیت اعتبار قیمت‌ها")', self.source)
        self.assertIn("تاریخ اعلام هر نرخ را کنار همان جدول بررسی کنید", self.source)
        self.assertIn("قیمت قطعی، موجودی و هزینه حمل هنگام سفارش با کارشناس تأیید می‌شود", self.source)

    def test_notice_is_inserted_after_header_when_present(self):
        self.assertIn('siteHeader.insertAdjacentElement("afterend",notice)', self.source)

    def test_notice_has_mobile_responsive_styles(self):
        self.assertIn("@media(max-width:600px)", self.source)
        self.assertIn(".ae-price-status-strip", self.source)

    def test_all_price_html_pages_load_the_shared_asset(self):
        pages = sorted((ROOT / "prices").rglob("*.html"))
        self.assertGreater(len(pages), 0)
        missing = [p.relative_to(ROOT).as_posix() for p in pages
                   if "/assets/site-footer.js" not in p.read_text(encoding="utf-8", errors="replace")]
        self.assertEqual(missing, [], f"Price pages missing shared footer/status asset: {missing}")

    def test_shared_footer_remains_idempotent(self):
        self.assertIn("window.__AHANEIFFEL_SITE_FOOTER__", self.source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
