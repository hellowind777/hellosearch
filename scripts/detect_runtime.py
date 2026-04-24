from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime import choose_route, detect_runtime_environment


def configure_stdout_utf8() -> None:
    """Force UTF-8 stdout on Windows terminals when supported."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for runtime detection."""

    parser = argparse.ArgumentParser(description="Detect HelloSearch runtime routing candidates.")
    parser.add_argument("--cwd", default=".", help="Workspace directory to inspect.")
    parser.add_argument("--needs-fetch", action="store_true", help="Require fetch capability in the routing decision.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a human-readable summary.")
    return parser


def render_text(report, decision) -> str:
    """Render a concise text report for local inspection."""

    lines = [
        f"Workspace root: {report.workspace_root}",
        f"Detected runtimes: {len(report.runtimes)}",
    ]

    if report.primary_runtime:
        lines.append(
            f"Primary runtime: {report.primary_runtime.host.value} (confidence {report.primary_runtime.confidence})"
        )
    else:
        lines.append("Primary runtime: none")

    for runtime in report.runtimes:
        lines.append(f"- {runtime.host.value}: {runtime.capabilities.to_dict()} | notes={len(runtime.notes)}")

    lines.append(
        f"Route: {decision.adapter_id} -> {decision.backend.value} | reason={decision.reason}"
    )
    return "\n".join(lines)


def main() -> int:
    """Run runtime detection and print the routing recommendation."""

    configure_stdout_utf8()
    parser = build_parser()
    args = parser.parse_args()

    report = detect_runtime_environment(Path(args.cwd))
    decision = choose_route(report, needs_fetch=args.needs_fetch)

    if args.json:
        payload = report.to_dict()
        payload["route_decision"] = decision.to_dict()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(render_text(report, decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
