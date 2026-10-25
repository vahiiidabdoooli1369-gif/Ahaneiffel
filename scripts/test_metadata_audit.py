#!/usr/bin/env python3
"""Regression tests for the report-only SEO metadata audit."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_internal_links", ROOT / "scripts" / "audit_internal_links.py")
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(AUDIT)


class MetadataAuditTests(unittest.TestCase):
    def audit(self, documents):
        paths = []
        with tempfile.TemporaryDirectory() as directory:
            for index, document in enumerate(documents):
                path = Path(directory) / f"page-{index}.html"
                path.write_text(document, encoding="utf-8")
                paths.append(path)
            with patch.object(AUDIT, "public_url", side_effect=lambda path: "/" + path.name):
                return AUDIT.audit_metadata_quality(paths)

    def test_duplicate_titles_and_descriptions_are_reported(self):
        docs = [
            '<html lang="fa"><head><title>راهنمای خرید پروفیل فولادی</title>'
            '<meta name="description" content="راهنمای کامل خرید پروفیل فولادی برای پروژه ساختمانی"></head></html>',
            '<html lang="fa"><head><title>راهنمای خرید پروفیل فولادی</title>'
            '<meta name="description" content="راهنمای کامل خرید پروفیل فولادی برای پروژه ساختمانی"></head></html>',
        ]
        issues = self.audit(docs)
        kinds = [kind for _, kind, _ in issues]
        self.assertEqual(kinds.count("duplicate-title"), 2)
        self.assertEqual(kinds.count("duplicate-meta-description"), 2)

    def test_missing_title_description_and_language_are_reported(self):
        issues = self.audit(["<html><head></head><body>صفحه آزمایشی</body></html>"])
        kinds = {kind for _, kind, _ in issues}
        self.assertTrue({"missing-title", "missing-meta-description", "missing-html-lang"} <= kinds)

    def test_multiple_and_empty_metadata_are_reported(self):
        document = (
            '<html lang="fa"><head><title></title><title>عنوان دوم برای صفحه آزمایشی</title>'
            '<meta name="description" content=""><meta name="description" content="توضیح دوم"></head></html>'
        )
        kinds = {kind for _, kind, _ in self.audit([document])}
        self.assertTrue({"multiple-titles", "multiple-meta-descriptions"} <= kinds)

    def test_length_boundaries_are_reported_without_mutating_pages(self):
        title = "عنوان"
        description = "توضیح"
        document = f'<html lang="fa"><head><title>{title}</title><meta name="description" content="{description}"></head></html>'
        issues = self.audit([document])
        kinds = {kind for _, kind, _ in issues}
        self.assertIn("short-title", kinds)
        self.assertIn("short-meta-description", kinds)
        self.assertIn("<title>عنوان</title>", document)


if __name__ == "__main__":
    unittest.main(verbosity=2)
