import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("audit_seo_metadata",ROOT/"scripts"/"audit_seo_metadata.py")
MODULE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class SeoMetadataTests(unittest.TestCase):
    def make_page(self, html):
        handle=tempfile.NamedTemporaryFile("w",encoding="utf-8",suffix=".html",dir=ROOT,delete=False)
        handle.write(html); handle.close()
        return Path(handle.name)

    def test_parser_extracts_title_description_h1_canonical(self):
        p=MODULE.PageParser()
        p.feed('<title>عنوان آزمایشی مناسب</title><meta name="description" content="شرح صفحه"><h1>تیتر</h1><link rel="canonical" href="https://example.com/">')
        self.assertEqual(p.title,"عنوان آزمایشی مناسب")
        self.assertEqual(p.description,["شرح صفحه"])
        self.assertEqual(p.h1_count,1)
        self.assertEqual(p.canonical,["https://example.com/"])

    def test_missing_and_length_flags(self):
        row=MODULE.inspect_sample({"title":"x","description":"y","h1_count":0,"canonical_count":0})
        self.assertEqual(set(row),{"title-too-short","description-too-short","missing-h1","missing-canonical"})

    def test_noindex_redirect_is_excluded_from_indexable_audit(self):
        path=self.make_page('<meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url=/target/"><title>Legacy URL</title>')
        try:
            row=MODULE.inspect(path)
            self.assertFalse(row["indexable_audit"])
            self.assertTrue(row["noindex"])
            self.assertTrue(row["meta_refresh"])
            self.assertEqual(row["issues"],[])
        finally:
            path.unlink(missing_ok=True)

    def test_duplicate_detection_marks_both_indexable_pages(self):
        a=self.make_page('<title>A sufficiently long title for this test</title><meta name="description" content="This is a sufficiently long description for the duplicate title regression test."><h1>A</h1><link rel="canonical" href="https://example.com/a">')
        b=self.make_page('<title>A sufficiently long title for this test</title><meta name="description" content="A different sufficiently long description for this duplicate title regression test."><h1>B</h1><link rel="canonical" href="https://example.com/b">')
        try:
            report=MODULE.audit([a,b])
            self.assertIn("duplicate-title",report["pages"][0]["issues"])
            self.assertIn("duplicate-title",report["pages"][1]["issues"])
        finally:
            a.unlink(missing_ok=True); b.unlink(missing_ok=True)

if __name__=="__main__": unittest.main(verbosity=2)
