from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.evidence import rank_sources


def configure_stdout_utf8() -> None:
    """Force UTF-8 stdout on Windows terminals when supported."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for source ranking."""

    parser = argparse.ArgumentParser(description="Normalize and rank HelloSearch sources.")
    parser.add_argument("query", help="Original user query.")
    parser.add_argument("--input", help="Path to a JSON file containing a list of sources.")
    parser.add_argument("--preferred-domain", action="append", default=[], help="Preferred domain hint.")
    return parser


def load_sources(input_path: str | None) -> list[dict]:
    """Load JSON source data from a file or stdin."""

    if input_path:
        raw = Path(input_path).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    data = json.loads(raw)
    return data.get("sources", data) if isinstance(data, dict) else data


def main() -> int:
    """Run source ranking and print ranked JSON."""

    configure_stdout_utf8()
    args = build_parser().parse_args()
    ranked = rank_sources(
        args.query,
        load_sources(args.input),
        preferred_domains=tuple(args.preferred_domain),
    )
    print(json.dumps([item.to_dict() for item in ranked], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
