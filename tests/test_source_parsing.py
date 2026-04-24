from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.source_parsing import parse_source_payload, split_answer_and_sources


class SourceParsingTests(unittest.TestCase):
    def test_split_answer_and_sources_from_function_call(self):
        answer, sources = split_answer_and_sources(
            'Verified result.\nreferences([{"title":"Docs","url":"https://docs.example.com/api"}])'
        )
        self.assertEqual(answer, "Verified result.")
        self.assertEqual(sources[0]["url"], "https://docs.example.com/api")

    def test_parse_source_payload_handles_python_like_lists(self):
        sources = parse_source_payload("[('Docs', 'https://docs.example.com/api')]")
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["url"], "https://docs.example.com/api")


if __name__ == "__main__":
    unittest.main()
