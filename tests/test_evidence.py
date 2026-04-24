from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.evidence import canonicalize_url, rank_sources


class EvidenceTests(unittest.TestCase):
    def test_canonicalize_url_drops_tracking(self):
        cleaned = canonicalize_url("https://example.com/docs?a=1&utm_source=test#part")
        self.assertEqual(cleaned, "https://example.com/docs?a=1")

    def test_rank_sources_prefers_docs_domain(self):
        ranked = rank_sources(
            "openai responses api parameters",
            [
                {"title": "Blog summary", "url": "https://random.example/blog/openai", "snippet": "overview"},
                {"title": "API reference", "url": "https://docs.example.com/responses", "snippet": "parameters and schema"},
            ],
            preferred_domains=("docs.",),
        )
        self.assertEqual(ranked[0].source.url, "https://docs.example.com/responses")

    def test_rank_sources_normalizes_output_url(self):
        ranked = rank_sources(
            "openai responses api parameters",
            [
                {"title": "API reference", "url": "https://docs.example.com/responses?utm_source=test", "snippet": "schema"},
            ],
        )
        self.assertEqual(ranked[0].source.url, "https://docs.example.com/responses")


if __name__ == "__main__":
    unittest.main()
