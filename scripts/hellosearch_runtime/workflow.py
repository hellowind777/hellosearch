from __future__ import annotations

from datetime import date
from pathlib import Path

from .detection import detect_runtime_environment
from .planning import SearchPlan, build_search_plan
from .router import choose_route


FETCH_KEYWORDS = ("api", "docs", "documentation", "参数", "pricing", "price", "release", "breaking", "issue", "官网")


def infer_fetch_need(question: str) -> bool:
    """Decide whether the workflow should assume page-level fetching."""

    lowered = question.lower()
    return any(keyword in lowered or keyword in question for keyword in FETCH_KEYWORDS)


def build_workflow_bundle(question: str, cwd: Path | None = None, today: date | None = None) -> dict:
    """Combine runtime routing, deterministic planning, and answer constraints."""

    report = detect_runtime_environment(cwd)
    search_plan: SearchPlan = build_search_plan(question, today=today)
    route_decision = choose_route(report, needs_fetch=infer_fetch_need(question))

    execution_steps = [
        "Run round 1 queries to map the landscape and locate primary sources.",
        "Open the strongest source pages listed in `fetch_targets` before answering.",
        "Run round 2 targeted queries to resolve gaps or contradictions.",
        "Rank and dedupe collected sources before synthesis.",
        "Write the final answer using the answer checklist.",
    ]

    return {
        "question": question,
        "runtime_report": report.to_dict(),
        "route_decision": route_decision.to_dict(),
        "search_plan": search_plan.to_dict(),
        "execution_steps": execution_steps,
    }
