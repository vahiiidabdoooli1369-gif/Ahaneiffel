#!/usr/bin/env python3
"""Offline regression tests for the live sitemap HTTP audit."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_live_sitemap", ROOT / "scripts" / "audit_live_sitemap.py")
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class LiveSitemapAuditTests(unittest.TestCase):
    def test_recurses_deduplicates_and_rejects_external_child_sitemaps(self):
        index = b"""<?xml version="1.0"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://ahaneiffel.top/sitemap-guides.xml</loc></sitemap>
          <sitemap><loc>https://example.org/foreign.xml</loc></sitemap>
        </sitemapindex>"""
        child = b"""<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://ahaneiffel.top/</loc></url>
          <url><loc>https://ahaneiffel.top/guides/</loc></url>
          <url><loc>https://ahaneiffel.top/</loc></url>
        </urlset>"""

        def fake_fetch(url):
            if url == "https://ahaneiffel.top/sitemap.xml":
                return 200, url, index
            if url == "https://ahaneiffel.top/sitemap-guides.xml":
                return 200, url, child
            raise AssertionError(f"unexpected fetch: {url}")

        with patch.object(AUDIT, "fetch", side_effect=fake_fetch):
            urls, errors = AUDIT.collect_sitemap_urls("https://ahaneiffel.top")

        self.assertEqual(urls, ["https://ahaneiffel.top/", "https://ahaneiffel.top/guides/"])
        self.assertTrue(any("off-host/non-HTTPS child sitemap rejected" in error for error in errors))

    def test_unexpected_xml_root_is_reported(self):
        with patch.object(AUDIT, "fetch", return_value=(200, "https://ahaneiffel.top/sitemap.xml", b"<wrong/>")):
            urls, errors = AUDIT.collect_sitemap_urls("https://ahaneiffel.top")
        self.assertEqual(urls, [])
        self.assertTrue(any("unexpected sitemap root element" in error for error in errors))

    def test_check_url_rejects_noncanonical_host_without_network_access(self):
        with patch.object(AUDIT, "fetch") as mocked_fetch:
            result = AUDIT.check_url("https://example.org/not-ours")
        self.assertEqual(result.status, "SKIP")
        mocked_fetch.assert_not_called()

    def test_http_error_is_reported_as_status(self):
        import urllib.error
        error = urllib.error.HTTPError(
            "https://ahaneiffel.top/missing/", 404, "Not Found", {}, None
        )
        with patch.object(AUDIT, "fetch", side_effect=error):
            result = AUDIT.check_url("https://ahaneiffel.top/missing/")
        self.assertEqual(result.status, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
