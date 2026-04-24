from __future__ import annotations

from datetime import date
from pathlib import Path

from .detection import detect_runtime_environment
from .planning import build_search_plan
from .router import choose_route


FETCH_KEYWORDS = ("api", "docs", "documentation", "参数", "pricing", "price", "release", "breaking", "issue", "官网")
MAP_KEYWORDS = ("site map", "sitemap", "文档站", "站点地图", "目录结构", "全站", "所有页面", "all docs", "all pages", "all endpoints")


def infer_fetch_need(question: str) -> bool:
    """Decide whether the workflow should assume page-level fetching."""

    lowered = question.lower()
    return any(keyword in lowered or keyword in question for keyword in FETCH_KEYWORDS)


def infer_map_need(question: str) -> bool:
    """Decide whether the workflow should ask for site-level mapping."""

    lowered = question.lower()
    return any(keyword in lowered or keyword in question for keyword in MAP_KEYWORDS)


def build_workflow_bundle(question: str, cwd: Path | None = None, today: date | None = None) -> dict:
    """Combine runtime routing, deterministic planning, and answer constraints."""

    report = detect_runtime_environment(cwd)
    search_plan = build_search_plan(question, today=today)
    needs_fetch = infer_fetch_need(question)
    needs_map = infer_map_need(question) or bool(search_plan.map_targets)
    route_decision = choose_route(report, needs_fetch=needs_fetch)

    execution_steps = [
        "Run round 1 queries to map the landscape and locate primary sources.",
        "Open the strongest source pages listed in `fetch_targets` before answering.",
        "Run round 2 targeted queries to resolve gaps or contradictions.",
    ]
    if needs_map:
        execution_steps.append("Use host-native site mapping when available to inventory relevant documentation pages.")
    execution_steps.extend(
        [
            "If the host returns mixed answer-plus-citation text, split sources before synthesis.",
            "Rank and dedupe collected sources before synthesis.",
            "Write the final answer using the answer checklist.",
        ]
    )

    capability_gaps: list[str] = []
    capabilities = route_decision.capabilities.to_dict()
    if needs_map and capabilities["map_site"] == "unavailable":
        capability_gaps.append("No confirmed host-native site-map capability is available.")
    if needs_fetch and capabilities["fetch"] == "unavailable":
        capability_gaps.append("No confirmed host-native fetch capability is available.")

    return {
        "question": question,
        "runtime_report": report.to_dict(),
        "route_decision": route_decision.to_dict(),
        "search_plan": search_plan.to_dict(),
        "needs_fetch": needs_fetch,
        "needs_map": needs_map,
        "capability_gaps": capability_gaps,
        "execution_steps": execution_steps,
    }
