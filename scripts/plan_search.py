from __future__ import annotations

import argparse
from datetime import date
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.planning import build_search_plan


def configure_stdout_utf8() -> None:
    """Force UTF-8 stdout on Windows terminals when supported."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for deterministic search planning."""

    parser = argparse.ArgumentParser(description="Build a deterministic HelloSearch query plan.")
    parser.add_argument("question", help="User question to transform into a search plan.")
    parser.add_argument("--today", help="Override relative-date expansion with YYYY-MM-DD.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    return parser


def render_text(plan: dict) -> str:
    """Render a compact human-readable plan."""

    lines = [
        f"Core question: {plan['core_question']}",
        f"Query type: {plan['query_type']}",
        f"Time sensitivity: {plan['time_sensitivity']}",
    ]
    intent = plan.get("intent", {})
    if intent.get("ambiguities"):
        lines.append(f"Ambiguities: {', '.join(intent['ambiguities'])}")
    if intent.get("unverified_terms"):
        lines.append(f"Unverified terms: {', '.join(intent['unverified_terms'])}")
    complexity = plan.get("complexity", {})
    if complexity:
        lines.append(
            f"Complexity: L{complexity['level']} | sub-queries={complexity['estimated_sub_queries']} | tool-calls={complexity['estimated_tool_calls']}"
        )
    if plan["exact_time_context"]:
        lines.append(f"Time context: {', '.join(plan['exact_time_context'])}")
    lines.append(f"Source priorities: {', '.join(plan['source_priorities'])}")
    for item in plan["rounds"]:
        lines.append(f"Round {item['round']}: {item['objective']}")
        for query in item["queries"]:
            lines.append(f"- {query['text']} [{query['goal']}]")
    if plan.get("map_targets"):
        lines.append(f"Map targets: {', '.join(plan['map_targets'])}")
    return "\n".join(lines)


def main() -> int:
    """Run the planning CLI."""

    configure_stdout_utf8()
    args = build_parser().parse_args()
    today = date.fromisoformat(args.today) if args.today else None
    plan = build_search_plan(args.question, today=today).to_dict()

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    print(render_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
