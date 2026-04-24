from __future__ import annotations

from datetime import date

from .planning_heuristics import (
    assess_complexity,
    build_answer_checklist,
    classify_query_type,
    detect_unverified_terms,
    infer_ambiguities,
    infer_domain_focus,
    infer_fetch_targets,
    infer_map_targets,
    infer_premise_validity,
    infer_preferred_domains,
    infer_source_priorities,
)
from .planning_types import (
    ExecutionPlan,
    SearchIntent,
    SearchPlan,
    SearchQuery,
    SearchRound,
    SearchStrategy,
    SearchSubQuery,
    ToolSelection,
)
from .time_utils import detect_time_sensitivity, expand_relative_time_context, resolve_base_date


def build_sub_queries(intent: SearchIntent, complexity_level: int, map_targets: tuple[str, ...]) -> tuple[SearchSubQuery, ...]:
    """Create a stable list of sub-queries from the search intent."""

    items = [
        SearchSubQuery("sq1", "Locate the strongest primary sources.", "Official pages or primary reporting.", "Do not answer from snippets alone.", "search"),
        SearchSubQuery("sq2", "Open and verify the decisive source pages.", "Page-level evidence with exact dates or parameters.", "Do not rely on secondary summaries.", "fetch", ("sq1",)),
    ]
    if intent.query_type == "comparative":
        items.append(SearchSubQuery("sq3", "Collect the same attributes for every option.", "A comparison table with matched fields.", "Do not compare mismatched evidence.", "search", ("sq2",)))
    if intent.query_type in {"analytical", "exploratory"}:
        items.append(SearchSubQuery("sq3", "Expand the search into supporting context.", "Additional primary or high-quality secondary evidence.", "Do not repeat already confirmed facts.", "search", ("sq2",)))
    if intent.unverified_terms:
        items.append(SearchSubQuery("sq4", "Verify external rankings or taxonomy labels first.", "Primary definition of the disputed label.", "Do not assume training-time labels are current.", "search", ("sq1",)))
    if map_targets:
        items.append(SearchSubQuery("sq5", "Map the relevant documentation site before drilling down.", "A site-level inventory of likely pages.", "Do not crawl unrelated site sections.", "map_site", ("sq1",)))
    limit = {1: 2, 2: 4, 3: 6}[complexity_level]
    return tuple(items[:limit])


def build_rounds(question: str, intent: SearchIntent, sub_queries: tuple[SearchSubQuery, ...]) -> tuple[SearchRound, ...]:
    """Create broad-first search rounds."""

    round_one = [
        SearchQuery(
            text=_normalize_query_text(question, intent.exact_time_context),
            goal="broad discovery",
            source_hint=intent.source_priorities[0] if intent.source_priorities else "",
            purpose=sub_queries[0].id,
        ),
        SearchQuery(
            text=f"{question.strip()} official source",
            goal="find the primary source",
            source_hint=intent.source_priorities[0] if intent.source_priorities else "",
            purpose=sub_queries[0].id,
        ),
    ]
    round_two: list[SearchQuery] = []
    if "official docs" in intent.source_priorities:
        round_two.append(SearchQuery(f"{question.strip()} official documentation", "verify against docs", "official docs", "sq2"))
    if "repo or changelog" in intent.source_priorities or "release notes" in intent.source_priorities:
        round_two.append(SearchQuery(f"{question.strip()} changelog OR release notes", "find version evidence", "release notes", "sq2"))
    for domain in intent.preferred_domains[:2]:
        round_two.append(SearchQuery(_render_domain_query(question.strip(), domain), "targeted domain check", domain, "sq2"))
    if intent.unverified_terms:
        round_two.append(SearchQuery(f"{intent.unverified_terms[0]} official definition", "verify external label", "primary definition", "sq4"))
    return (
        SearchRound(1, "Map the landscape and find primary sources.", tuple(_trim_queries(round_one))),
        SearchRound(2, "Verify with targeted primary-source searches.", tuple(_trim_queries(round_two))),
    )


def build_strategy(rounds: tuple[SearchRound, ...], complexity_level: int) -> SearchStrategy:
    """Build the execution strategy summary."""

    approach = "broad_first" if complexity_level >= 2 else "targeted"
    search_terms = tuple(query for item in rounds for query in item.queries)
    fallback = "If primary sources remain weak, widen one round to strong secondary reporting and re-verify the deciding fact."
    return SearchStrategy(approach=approach, search_terms=search_terms, fallback_plan=fallback)


def build_tool_selection(sub_queries: tuple[SearchSubQuery, ...], fetch_targets: tuple[str, ...], map_targets: tuple[str, ...]) -> tuple[ToolSelection, ...]:
    """Choose the preferred host-native tool family for each sub-query."""

    selections: list[ToolSelection] = []
    for item in sub_queries:
        if item.tool_hint == "map_site":
            selections.append(ToolSelection(item.id, "map_site", "Map the relevant site before opening specific pages.", {"targets": list(map_targets)}))
        elif item.tool_hint == "fetch":
            selections.append(ToolSelection(item.id, "fetch", "Open full pages for decisive evidence.", {"targets": list(fetch_targets)}))
        else:
            selections.append(ToolSelection(item.id, "search", "Use host-native web search to gather candidate sources."))
    return tuple(selections)


def build_execution_plan(sub_queries: tuple[SearchSubQuery, ...]) -> ExecutionPlan:
    """Recommend an execution order."""

    first_wave = tuple(item.id for item in sub_queries if not item.depends_on)
    sequential = tuple(item.id for item in sub_queries if item.depends_on)
    estimated_rounds = (2 if first_wave else 1) + (1 if sequential else 0)
    parallel = (first_wave,) if first_wave else ()
    return ExecutionPlan(parallel=parallel, sequential=sequential, estimated_rounds=estimated_rounds)


def build_search_plan(question: str, today: date | None = None) -> SearchPlan:
    """Create a deterministic multi-step search plan from one user question."""

    anchor = resolve_base_date(today)
    query_type = classify_query_type(question)
    time_sensitivity = detect_time_sensitivity(question)
    exact_time_context = tuple(expand_relative_time_context(question, anchor))
    source_priorities = infer_source_priorities(question)
    preferred_domains = infer_preferred_domains(question)
    ambiguities = infer_ambiguities(question)
    unverified_terms = detect_unverified_terms(question)
    map_targets = infer_map_targets(question, preferred_domains, source_priorities)
    intent = SearchIntent(
        core_question=question.strip(),
        query_type=query_type,
        time_sensitivity=time_sensitivity,
        exact_time_context=exact_time_context,
        source_priorities=source_priorities,
        preferred_domains=preferred_domains,
        domain=infer_domain_focus(question, preferred_domains),
        premise_valid=infer_premise_validity(question, ambiguities, unverified_terms),
        ambiguities=ambiguities,
        unverified_terms=unverified_terms,
    )
    complexity = assess_complexity(query_type, time_sensitivity, ambiguities, unverified_terms, map_targets)
    sub_queries = build_sub_queries(intent, complexity.level, map_targets)
    rounds = build_rounds(question, intent, sub_queries)
    fetch_targets = infer_fetch_targets(source_priorities)
    return SearchPlan(
        intent=intent,
        complexity=complexity,
        rounds=rounds,
        sub_queries=sub_queries,
        strategy=build_strategy(rounds, complexity.level),
        tool_selection=build_tool_selection(sub_queries, fetch_targets, map_targets),
        execution=build_execution_plan(sub_queries),
        fetch_targets=fetch_targets,
        map_targets=map_targets,
        answer_checklist=build_answer_checklist(query_type, time_sensitivity, map_targets),
    )


def _normalize_query_text(question: str, time_context: tuple[str, ...]) -> str:
    return f"{question.strip()} ({'; '.join(time_context)})" if time_context else question.strip()


def _trim_queries(queries: list[SearchQuery], limit: int = 4) -> list[SearchQuery]:
    seen: set[str] = set()
    result: list[SearchQuery] = []
    for item in queries:
        if item.text in seen:
            continue
        seen.add(item.text)
        result.append(item)
    return result[:limit]


def _render_domain_query(question: str, domain: str) -> str:
    return f"{question} site:{domain}" if "." in domain and not domain.endswith(".") else f"{question} {domain}"
