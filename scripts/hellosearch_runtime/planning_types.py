from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchQuery:
    """One concrete query to run in a given round."""

    text: str
    goal: str
    source_hint: str = ""
    purpose: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SearchRound:
    """Batch of related searches executed in one stage."""

    round: int
    objective: str
    queries: tuple[SearchQuery, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "round": self.round,
            "objective": self.objective,
            "queries": [query.to_dict() for query in self.queries],
        }


@dataclass(frozen=True)
class SearchIntent:
    """Normalized description of the user's search intent."""

    core_question: str
    query_type: str
    time_sensitivity: str
    exact_time_context: tuple[str, ...] = ()
    source_priorities: tuple[str, ...] = ()
    preferred_domains: tuple[str, ...] = ()
    domain: str = ""
    premise_valid: bool | None = None
    ambiguities: tuple[str, ...] = ()
    unverified_terms: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["premise_valid"] = self.premise_valid
        return data


@dataclass(frozen=True)
class SearchComplexity:
    """Estimated effort required to answer the question well."""

    level: int
    estimated_sub_queries: int
    estimated_tool_calls: int
    justification: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SearchSubQuery:
    """One scoped sub-problem inside the overall search task."""

    id: str
    goal: str
    expected_output: str
    boundary: str
    tool_hint: str = ""
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SearchStrategy:
    """How the search should be executed across rounds."""

    approach: str
    search_terms: tuple[SearchQuery, ...] = ()
    fallback_plan: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "approach": self.approach,
            "search_terms": [item.to_dict() for item in self.search_terms],
            "fallback_plan": self.fallback_plan,
        }


@dataclass(frozen=True)
class ToolSelection:
    """Recommended host-native tool family for one sub-query."""

    sub_query_id: str
    tool: str
    reason: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionPlan:
    """Recommended execution order for the search task."""

    parallel: tuple[tuple[str, ...], ...] = ()
    sequential: tuple[str, ...] = ()
    estimated_rounds: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "parallel": [list(group) for group in self.parallel],
            "sequential": list(self.sequential),
            "estimated_rounds": self.estimated_rounds,
        }


@dataclass(frozen=True)
class SearchPlan:
    """Deterministic search plan used before native tool invocation."""

    intent: SearchIntent
    complexity: SearchComplexity
    rounds: tuple[SearchRound, ...] = ()
    sub_queries: tuple[SearchSubQuery, ...] = ()
    strategy: SearchStrategy = field(default_factory=lambda: SearchStrategy(approach="broad_first"))
    tool_selection: tuple[ToolSelection, ...] = ()
    execution: ExecutionPlan = field(default_factory=ExecutionPlan)
    fetch_targets: tuple[str, ...] = ()
    map_targets: tuple[str, ...] = ()
    answer_checklist: tuple[str, ...] = ()

    @property
    def core_question(self) -> str:
        return self.intent.core_question

    @property
    def query_type(self) -> str:
        return self.intent.query_type

    @property
    def time_sensitivity(self) -> str:
        return self.intent.time_sensitivity

    @property
    def exact_time_context(self) -> tuple[str, ...]:
        return self.intent.exact_time_context

    @property
    def source_priorities(self) -> tuple[str, ...]:
        return self.intent.source_priorities

    @property
    def preferred_domains(self) -> tuple[str, ...]:
        return self.intent.preferred_domains

    def to_dict(self) -> dict[str, Any]:
        return {
            "core_question": self.core_question,
            "query_type": self.query_type,
            "time_sensitivity": self.time_sensitivity,
            "exact_time_context": list(self.exact_time_context),
            "source_priorities": list(self.source_priorities),
            "preferred_domains": list(self.preferred_domains),
            "intent": self.intent.to_dict(),
            "complexity": self.complexity.to_dict(),
            "rounds": [item.to_dict() for item in self.rounds],
            "sub_queries": [item.to_dict() for item in self.sub_queries],
            "strategy": self.strategy.to_dict(),
            "tool_selection": [item.to_dict() for item in self.tool_selection],
            "execution": self.execution.to_dict(),
            "fetch_targets": list(self.fetch_targets),
            "map_targets": list(self.map_targets),
            "answer_checklist": list(self.answer_checklist),
        }
