import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("audit_seo_metadata",ROOT/"scripts"/"audit_seo_metadata.py")
MODULE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class SeoMetadataTests(unittest.TestCase):
    def test_parser_extracts_title_description_h1_canonical(self):
        p=MODULE.PageParser()
        p.feed('<title>عنوان آزمایشی مناسب</title><meta name="description" content="شرح صفحه"><h1>تیتر</h1><link rel="canonical" href="https://example.com/">')
        self.assertEqual(p.title,"عنوان آزمایشی مناسب")
        self.assertEqual(p.description,["شرح صفحه"])
        self.assertEqual(p.h1_count,1)
        self.assertEqual(p.canonical,["https://example.com/"])
    def test_missing_and_length_flags(self):
        row=MODULE.inspect_sample({"title":"x","description":"y","h1_count":0,"canonical":[]})
        self.assertEqual(set(row),{"title-too-short","description-too-short","missing-h1","missing-canonical"})
    def test_duplicate_detection(self):
        a={"path":"a.html","title":"Same title","description":"Same description","issues":[]}
        b={"path":"b.html","title":"Same title","description":"Different description","issues":[]}
        rows=[a,b]
        from collections import defaultdict
        for key in ("title","description"):
            seen=defaultdict(list)
            for row in rows:
                v=row[key].strip().casefold()
                if v: seen[v].append(row["path"])
            for group in seen.values():
                if len(group)>1:
                    for row in rows:
                        if row["path"] in group: row["issues"].append("duplicate-"+key)
        self.assertIn("duplicate-title",a["issues"])
        self.assertNotIn("duplicate-title",b["issues"])

if __name__=="__main__": unittest.main(verbosity=2)
