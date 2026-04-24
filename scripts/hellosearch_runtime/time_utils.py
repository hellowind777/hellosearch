from __future__ import annotations

from datetime import date, timedelta


TIME_KEYWORDS = {
    "realtime": ("今天", "today", "now", "current", "实时", "现在", "latest", "最新"),
    "recent": ("recent", "recently", "最近", "近期", "this week", "this month", "本周", "本月"),
    "historical": ("去年", "last year", "history", "historical", "过往", "archive"),
}


def resolve_base_date(base_date: date | None = None) -> date:
    """Return the effective date used for relative-time expansion."""

    return base_date or date.today()


def detect_time_sensitivity(query: str) -> str:
    """Classify the query by simple relative-time heuristics."""

    lowered = query.lower()
    for label, keywords in TIME_KEYWORDS.items():
        if any(keyword in query or keyword in lowered for keyword in keywords):
            return label
    return "irrelevant"


def expand_relative_time_context(query: str, base_date: date | None = None) -> list[str]:
    """Convert common relative-time phrases into exact date guidance."""

    today = resolve_base_date(base_date)
    lowered = query.lower()
    notes: list[str] = []

    if "today" in lowered or "今天" in query:
        notes.append(f"today={today.isoformat()}")
    if "yesterday" in lowered or "昨天" in query:
        notes.append(f"yesterday={(today - timedelta(days=1)).isoformat()}")
    if "tomorrow" in lowered or "明天" in query:
        notes.append(f"tomorrow={(today + timedelta(days=1)).isoformat()}")
    if "this week" in lowered or "本周" in query:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        notes.append(f"this_week={start.isoformat()}..{end.isoformat()}")
    if "this month" in lowered or "本月" in query:
        start = today.replace(day=1)
        notes.append(f"this_month={start.isoformat()}..{today.isoformat()}")
    if any(token in lowered or token in query for token in ("current", "now", "现在", "目前", "latest", "最新", "recent", "最近")):
        notes.append(f"freshness_anchor={today.isoformat()}")
    return notes
