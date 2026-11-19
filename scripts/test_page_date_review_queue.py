import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("review_queue",ROOT/"scripts"/"build_page_date_review_queue.py")
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
class ReviewQueueTests(unittest.TestCase):
    def test_price_pages_are_highest_priority(self):
        self.assertEqual(module.classify("prices/rebar/index.html")[0],1)
    def test_product_detail_below_product_hub(self):
        self.assertLess(module.classify("products/rebar/index.html")[0],module.classify("products/rebar/10/index.html")[0])
    def test_only_flagged_pages_enter_queue(self):
        data=module.build({"page_count":2,"pages":[{"path":"prices/index.html","issues":["missing-visible-date"]},{"path":"products/rebar/index.html","issues":[]}]})
        self.assertEqual(data["pages_needing_review"],1)
        self.assertEqual(data["queue"][0]["review_status"],"needs_human_content_review")
    def test_git_date_is_not_treated_as_verified_review(self):
        data=module.build({"pages":[{"path":"guides/x/index.html","issues":["missing-visible-date"],"expected_jalali":"1405/08/28"}]})
        self.assertIn("not proof",data["policy"])
if __name__=="__main__": unittest.main(verbosity=2)
