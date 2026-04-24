from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.evidence import split_answer_and_normalize_sources


def configure_stdout_utf8() -> None:
    """Force UTF-8 stdout on Windows terminals when supported."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for source extraction."""

    parser = argparse.ArgumentParser(description="Split answer text from embedded citation blocks and normalize the sources.")
    parser.add_argument("--input", help="Path to a text or markdown file.")
    parser.add_argument("--text", help="Inline text to parse.")
    return parser


def load_text(args: argparse.Namespace) -> str:
    """Load the source text from CLI args or stdin."""

    if args.text:
        return args.text
    if args.input:
        return Path(args.input).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    """Run source extraction and print JSON."""

    configure_stdout_utf8()
    args = build_parser().parse_args()
    answer, sources = split_answer_and_normalize_sources(load_text(args))
    payload = {
        "answer": answer,
        "sources_count": len(sources),
        "sources": [item.to_dict() for item in sources],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
