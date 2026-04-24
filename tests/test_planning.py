from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.planning import build_search_plan


class PlanningTests(unittest.TestCase):
    def test_build_search_plan_expands_relative_time(self):
        plan = build_search_plan("Use hellosearch to verify today's NVIDIA news", today=date(2026, 4, 24))
        self.assertEqual(plan.time_sensitivity, "realtime")
        self.assertIn("today=2026-04-24", plan.exact_time_context)
        self.assertGreaterEqual(len(plan.rounds), 2)

    def test_build_search_plan_adds_docs_priority(self):
        plan = build_search_plan("查官网文档，确认这个 API 现在的参数", today=date(2026, 4, 24))
        self.assertIn("official docs", plan.source_priorities)
        self.assertIn("freshness_anchor=2026-04-24", plan.exact_time_context)
        self.assertIn("official documentation page", plan.fetch_targets)

    def test_build_search_plan_adds_complexity_and_sub_queries(self):
        plan = build_search_plan("Use hellosearch to compare these three API products and verify the latest pricing", today=date(2026, 4, 24))
        self.assertGreaterEqual(plan.complexity.level, 2)
        self.assertGreaterEqual(len(plan.sub_queries), 3)
        self.assertEqual(plan.strategy.approach, "broad_first")

    def test_build_search_plan_adds_map_target_for_site_inventory(self):
        plan = build_search_plan("Use hellosearch to map all docs pages for site:docs.example.com and find the current API limits", today=date(2026, 4, 24))
        self.assertIn("docs.example.com", plan.map_targets)
        self.assertTrue(any(item.tool == "map_site" for item in plan.tool_selection))


if __name__ == "__main__":
    unittest.main()
