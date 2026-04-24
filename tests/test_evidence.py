from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.evidence import canonicalize_url, rank_sources, split_answer_and_normalize_sources


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

    def test_split_answer_and_normalize_sources_from_heading_block(self):
        answer, sources = split_answer_and_normalize_sources(
            "Use the official docs.\n\nSources:\n- [API docs](https://docs.example.com/api?utm_source=test)\n- https://github.com/example/project"
        )
        self.assertEqual(answer, "Use the official docs.")
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].url, "https://docs.example.com/api")


if __name__ == "__main__":
    unittest.main()
