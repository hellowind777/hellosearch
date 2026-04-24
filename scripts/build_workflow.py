from __future__ import annotations

import argparse
from datetime import date
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.workflow import build_workflow_bundle


def configure_stdout_utf8() -> None:
    """Force UTF-8 stdout on Windows terminals when supported."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the combined workflow bundle."""

    parser = argparse.ArgumentParser(description="Build a full HelloSearch workflow bundle.")
    parser.add_argument("question", help="Question to execute with HelloSearch.")
    parser.add_argument("--cwd", default=".", help="Workspace root used for runtime detection.")
    parser.add_argument("--today", help="Override relative-date expansion with YYYY-MM-DD.")
    return parser


def main() -> int:
    """Run detection plus planning and print one JSON workflow bundle."""

    configure_stdout_utf8()
    args = build_parser().parse_args()
    today = date.fromisoformat(args.today) if args.today else None
    bundle = build_workflow_bundle(args.question, cwd=Path(args.cwd), today=today)
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
