from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

from .time_utils import detect_time_sensitivity, expand_relative_time_context, resolve_base_date


@dataclass(frozen=True)
class SearchQuery:
    """One concrete query to run in a given round."""

    text: str
    goal: str
    source_hint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SearchRound:
    """Batch of related searches executed in one stage."""

    round: int
    objective: str
    queries: tuple[SearchQuery, ...]

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "objective": self.objective,
            "queries": [query.to_dict() for query in self.queries],
        }


@dataclass(frozen=True)
class SearchPlan:
    """Deterministic search plan used before native tool invocation."""

    core_question: str
    query_type: str
    time_sensitivity: str
    exact_time_context: tuple[str, ...] = ()
    source_priorities: tuple[str, ...] = ()
    preferred_domains: tuple[str, ...] = ()
    rounds: tuple[SearchRound, ...] = ()
    fetch_targets: tuple[str, ...] = ()
    answer_checklist: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "core_question": self.core_question,
            "query_type": self.query_type,
            "time_sensitivity": self.time_sensitivity,
            "exact_time_context": list(self.exact_time_context),
            "source_priorities": list(self.source_priorities),
            "preferred_domains": list(self.preferred_domains),
            "rounds": [item.to_dict() for item in self.rounds],
            "fetch_targets": list(self.fetch_targets),
            "answer_checklist": list(self.answer_checklist),
        }


def classify_query_type(question: str) -> str:
    """Map a question to a simple search intent family."""

    lowered = question.lower()
    if any(marker in lowered for marker in ("vs", "compare", "difference", "区别", "对比")):
        return "comparative"
    if any(marker in lowered for marker in ("why", "how", "analysis", "分析", "原因")):
        return "analytical"
    if any(marker in lowered for marker in ("overview", "landscape", "有哪些", "盘点")):
        return "exploratory"
    return "factual"


def infer_source_priorities(question: str) -> tuple[str, ...]:
    """Choose primary source categories based on the task shape."""

    lowered = question.lower()
    priorities: list[str] = []
    if any(token in lowered for token in ("api", "sdk", "doc", "docs", "documentation", "参数", "用法")):
        priorities.extend(["official docs", "repo or changelog"])
    if any(token in lowered for token in ("price", "pricing", "套餐", "费用", "报价")):
        priorities.extend(["official pricing", "official faq"])
    if any(token in lowered for token in ("release", "breaking", "bug", "issue", "版本", "更新日志")):
        priorities.extend(["release notes", "repository issues"])
    if any(token in lowered for token in ("news", "latest", "最新", "融资", "发布")):
        priorities.extend(["official announcement", "primary reporting"])
    priorities.extend(["official docs", "primary reporting"])
    return tuple(_unique_keep_order(priorities))


def infer_preferred_domains(question: str) -> tuple[str, ...]:
    """Extract lightweight domain hints for later scoring."""

    lowered = question.lower()
    domains: list[str] = []
    if "github" in lowered or "repo" in lowered or "仓库" in question:
        domains.append("github.com")
    return tuple(_unique_keep_order(domains))


def _normalize_query_text(question: str, time_context: tuple[str, ...]) -> str:
    if not time_context:
        return question.strip()
    return f"{question.strip()} ({'; '.join(time_context)})"


def _build_round_one_queries(question: str, time_context: tuple[str, ...], source_priorities: tuple[str, ...]) -> tuple[SearchQuery, ...]:
    normalized = _normalize_query_text(question, time_context)
    queries = [
        SearchQuery(normalized, "broad discovery", source_priorities[0] if source_priorities else ""),
    ]
    if source_priorities:
        queries.append(SearchQuery(f"{question.strip()} official source", "find primary source", source_priorities[0]))
    return tuple(_trim_queries(queries))


def _build_round_two_queries(question: str, source_priorities: tuple[str, ...], preferred_domains: tuple[str, ...]) -> tuple[SearchQuery, ...]:
    queries: list[SearchQuery] = []
    if "official docs" in source_priorities:
        queries.append(SearchQuery(f"{question.strip()} official documentation", "verify against docs", "official docs"))
    if "repo or changelog" in source_priorities or "release notes" in source_priorities:
        queries.append(SearchQuery(f"{question.strip()} changelog OR release notes", "find version evidence", "release notes"))
    if preferred_domains:
        for domain in preferred_domains[:2]:
            queries.append(SearchQuery(_render_domain_query(question.strip(), domain), "targeted domain check", domain))
    return tuple(_trim_queries(queries))


def _trim_queries(queries: list[SearchQuery], limit: int = 4) -> list[SearchQuery]:
    return _unique_keep_order(queries)[:limit]


def _render_domain_query(question: str, domain: str) -> str:
    if "." in domain and not domain.endswith("."):
        return f"{question} site:{domain}"
    return f"{question} {domain}"


def _unique_keep_order(items: list) -> list:
    seen: set = set()
    result: list = []
    for item in items:
        key = item if isinstance(item, str) else item.text
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


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
    targets = [mapping[item] for item in source_priorities if item in mapping]
    return tuple(_unique_keep_order(targets))


def build_answer_checklist(query_type: str, time_sensitivity: str) -> tuple[str, ...]:
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
    return tuple(checklist)


def build_search_plan(question: str, today: date | None = None) -> SearchPlan:
    """Create a deterministic two-round search plan from one user question."""

    anchor = resolve_base_date(today)
    query_type = classify_query_type(question)
    time_sensitivity = detect_time_sensitivity(question)
    exact_time_context = tuple(expand_relative_time_context(question, anchor))
    source_priorities = infer_source_priorities(question)
    preferred_domains = infer_preferred_domains(question)

    rounds = (
        SearchRound(
            round=1,
            objective="Map the landscape and find primary sources.",
            queries=_build_round_one_queries(question, exact_time_context, source_priorities),
        ),
        SearchRound(
            round=2,
            objective="Verify with targeted primary-source searches.",
            queries=_build_round_two_queries(question, source_priorities, preferred_domains),
        ),
    )

    return SearchPlan(
        core_question=question.strip(),
        query_type=query_type,
        time_sensitivity=time_sensitivity,
        exact_time_context=exact_time_context,
        source_priorities=source_priorities,
        preferred_domains=preferred_domains,
        rounds=rounds,
        fetch_targets=infer_fetch_targets(source_priorities),
        answer_checklist=build_answer_checklist(query_type, time_sensitivity),
    )
