from __future__ import annotations

from dataclasses import dataclass
import re

from .planning_types import SearchComplexity


_AMBIGUOUS_REFERENCES = ("this", "that", "these", "those", "it", "they", "这个", "这个库", "这个产品", "这些", "它", "它们")
_UNVERIFIED_MARKERS = ("ccf", "gartner", "fortune 500", "owasp", "magic quadrant", "iso 27001", "top 10", "排名")
_MAP_KEYWORDS = ("site map", "sitemap", "site structure", "文档站", "站点地图", "目录结构", "全站", "所有页面", "所有文档", "all docs", "all pages", "all endpoints")


def classify_query_type(question: str) -> str:
    """Map a question to a simple search intent family."""

    lowered = question.lower()
    if any(marker in lowered for marker in ("vs", "compare", "difference", "区别", "对比")):
        return "comparative"
    if any(marker in lowered for marker in ("why", "how", "analysis", "analyze", "分析", "原因")):
        return "analytical"
    if any(marker in lowered for marker in ("overview", "landscape", "有哪些", "盘点", "all", "全集")):
        return "exploratory"
    return "factual"


def infer_source_priorities(question: str) -> tuple[str, ...]:
    """Choose primary source categories based on the task shape."""

    lowered = question.lower()
    priorities: list[str] = []
    if any(token in lowered for token in ("api", "sdk", "doc", "docs", "documentation", "参数", "用法", "官网")):
        priorities.extend(["official docs", "repo or changelog"])
    if any(token in lowered for token in ("price", "pricing", "套餐", "费用", "报价")):
        priorities.extend(["official pricing", "official faq"])
    if any(token in lowered for token in ("release", "breaking", "bug", "issue", "版本", "更新日志", "changelog")):
        priorities.extend(["release notes", "repository issues"])
    if any(token in lowered for token in ("news", "latest", "最新", "融资", "发布", "announcement")):
        priorities.extend(["official announcement", "primary reporting"])
    priorities.extend(["official docs", "primary reporting"])
    return tuple(_unique_keep_order(priorities))


def infer_preferred_domains(question: str) -> tuple[str, ...]:
    """Extract lightweight domain hints for later scoring."""

    lowered = question.lower()
    domains: list[str] = []
    domains.extend(re.findall(r"site:([a-z0-9.-]+\.[a-z]{2,})", lowered))
    if "github" in lowered or "repo" in lowered or "仓库" in question:
        domains.append("github.com")
    return tuple(_unique_keep_order(domains))


def infer_domain_focus(question: str, preferred_domains: tuple[str, ...]) -> str:
    """Infer the main content domain the search should center on."""

    if preferred_domains:
        return preferred_domains[0]
    lowered = question.lower()
    if any(token in lowered for token in ("api", "sdk", "docs", "documentation", "参数", "文档")):
        return "documentation"
    if any(token in lowered for token in ("price", "pricing", "费用", "报价")):
        return "pricing"
    if any(token in lowered for token in ("news", "announcement", "发布", "动态")):
        return "news"
    return ""


def infer_ambiguities(question: str) -> tuple[str, ...]:
    """Surface phrasing that likely depends on missing context."""

    lowered = question.lower()
    word_hits = set(re.findall(r"\b[a-z]+\b", lowered))
    ambiguities: list[str] = []
    if any(
        (token in question if any("\u4e00" <= char <= "\u9fff" for char in token) else token in word_hits)
        for token in _AMBIGUOUS_REFERENCES
    ):
        ambiguities.append("The question appears to reference an unstated object or prior context.")
    if any(token in lowered for token in ("best", "top", "better", "最强", "最好")) and not any(
        token in lowered for token in ("for ", "用于", "场景", "criteria", "标准")
    ):
        ambiguities.append("Ranking language is present, but evaluation criteria are not explicit.")
    return tuple(_unique_keep_order(ambiguities))


def detect_unverified_terms(question: str) -> tuple[str, ...]:
    """Identify external classifications that should be verified before use."""

    lowered = question.lower()
    return tuple(term for term in _UNVERIFIED_MARKERS if term in lowered or term in question)


def infer_premise_validity(question: str, ambiguities: tuple[str, ...], unverified_terms: tuple[str, ...]) -> bool | None:
    """Return best-effort premise validity."""

    if ambiguities:
        return None
    lowered = question.lower()
    if any(token in lowered for token in ("rumor", "传闻", "supposedly", "allegedly")):
        return None
    if unverified_terms and any(token in lowered for token in ("is", "属于", "算不算", "是否")):
        return None
    return True


def infer_map_targets(question: str, preferred_domains: tuple[str, ...], source_priorities: tuple[str, ...]) -> tuple[str, ...]:
    """Decide whether site mapping should be part of the workflow."""

    lowered = question.lower()
    if not any(token in lowered or token in question for token in _MAP_KEYWORDS):
        return ()
    targets = list(preferred_domains)
    if not targets and "official docs" in source_priorities:
        targets.append("official documentation site")
    return tuple(_unique_keep_order(targets))


def assess_complexity(
    query_type: str,
    time_sensitivity: str,
    ambiguities: tuple[str, ...],
    unverified_terms: tuple[str, ...],
    map_targets: tuple[str, ...],
) -> SearchComplexity:
    """Estimate how much structure the task needs."""

    score = 0
    reasons: list[str] = []
    if query_type in {"comparative", "analytical", "exploratory"}:
        score += 1
        reasons.append(f"{query_type} question shape")
    if time_sensitivity in {"realtime", "recent"}:
        score += 1
        reasons.append("time-sensitive verification")
    if ambiguities:
        score += 1
        reasons.append("needs ambiguity handling")
    if unverified_terms:
        score += 1
        reasons.append("contains external labels that should be verified first")
    if map_targets:
        score += 1
        reasons.append("benefits from site-level mapping")

    level = 1 if score <= 1 else 2 if score <= 3 else 3
    estimated_sub_queries = {1: 2, 2: 4, 3: 6}[level]
    estimated_tool_calls = {1: 4, 2: 8, 3: 12}[level]
    return SearchComplexity(
        level=level,
        estimated_sub_queries=estimated_sub_queries,
        estimated_tool_calls=estimated_tool_calls,
        justification=", ".join(reasons) if reasons else "single-pass factual lookup",
    )


def infer_fetch_targets(source_priorities: tuple[str, ...]) -> tuple[str, ...]:
    """Map source priorities to concrete page types that should be opened."""

    mapping = {
        "official docs": "official documentation page",
        "repo or changelog": "repository release or changelog page",
        "release notes": "release notes page",
        "official pricing": "official pricing page",
        "official announcement": "official announcement page",
        "primary reporting": "best-sourced article page",
    }
    return tuple(_unique_keep_order([mapping[item] for item in source_priorities if item in mapping]))


def build_answer_checklist(query_type: str, time_sensitivity: str, map_targets: tuple[str, ...]) -> tuple[str, ...]:
    """Return a stable checklist for answer synthesis."""

    checklist = [
        "Lead with the strongest supported conclusion.",
        "State exact dates for time-sensitive facts.",
        "Separate confirmed facts from inference.",
        "Link primary sources when available.",
    ]
    if query_type == "comparative":
        checklist.append("Compare the same attributes for every option.")
    if time_sensitivity in {"realtime", "recent"}:
        checklist.append("Call out whether any source may already be stale.")
    if map_targets:
        checklist.append("Mention whether the answer covered the full relevant site or only sampled pages.")
    return tuple(checklist)


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
