from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import SourceRecord


TRACKING_PREFIXES = ("utm_", "spm", "fbclid", "gclid")


@dataclass(frozen=True)
class RankedSource:
    """Normalized source plus relevance score and reasoning."""

    source: SourceRecord
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self.source)
        data["score"] = round(self.score, 3)
        data["reasons"] = list(self.reasons)
        return data


def canonicalize_url(url: str) -> str:
    """Drop fragments and tracking parameters for stable dedupe."""

    if not url:
        return ""
    parts = urlsplit(url.strip())
    clean_query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(TRACKING_PREFIXES)
    ]
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, urlencode(clean_query), ""))


def normalize_sources(raw_sources: list[dict | SourceRecord]) -> list[SourceRecord]:
    """Convert mixed source inputs into normalized `SourceRecord` objects."""

    normalized: list[SourceRecord] = []
    seen: set[str] = set()

    for item in raw_sources:
        source = item if isinstance(item, SourceRecord) else SourceRecord(
            title=(item or {}).get("title", ""),
            url=(item or {}).get("url", ""),
            snippet=(item or {}).get("snippet") or (item or {}).get("description", ""),
            provider=(item or {}).get("provider", ""),
            published_at=(item or {}).get("published_at", ""),
            retrieved_at=(item or {}).get("retrieved_at", ""),
        )
        key = canonicalize_url(source.url)
        if not key or key in seen:
            continue
        seen.add(key)
        normalized.append(
            SourceRecord(
                title=source.title,
                url=key,
                snippet=source.snippet,
                provider=source.provider,
                published_at=source.published_at,
                retrieved_at=source.retrieved_at,
            )
        )
    return normalized


def _domain_bonus(url: str, preferred_domains: tuple[str, ...]) -> tuple[float, list[str]]:
    lowered = url.lower()
    score = 0.0
    reasons: list[str] = []
    for domain in preferred_domains:
        if domain.lower() in lowered:
            score += 0.35
            reasons.append(f"matched preferred domain `{domain}`")
    if any(token in lowered for token in ("docs.", "developer.", "/docs")):
        score += 0.25
        reasons.append("looks like an official documentation page")
    if "github.com" in lowered:
        score += 0.18
        reasons.append("repository-hosted source")
    if lowered.endswith(".gov") or ".gov/" in lowered or lowered.endswith(".edu") or ".edu/" in lowered:
        score += 0.2
        reasons.append("government or academic domain")
    return score, reasons


def _text_bonus(query: str, source: SourceRecord) -> tuple[float, list[str]]:
    tokens = {token.lower() for token in query.split() if len(token) > 2}
    haystack = f"{source.title} {source.snippet}".lower()
    hits = sum(1 for token in tokens if token in haystack)
    if hits <= 0:
        return 0.0, []
    return min(0.4, hits * 0.08), [f"title or snippet matched {hits} query tokens"]


def _date_bonus(published_at: str) -> tuple[float, list[str]]:
    if not published_at:
        return 0.0, []
    try:
        parsed = parsedate_to_datetime(published_at)
    except (TypeError, ValueError, IndexError):
        try:
            parsed = date.fromisoformat(published_at)
        except ValueError:
            return 0.0, []
        age_days = max(0, (date.today() - parsed).days)
    else:
        age_days = max(0, (date.today() - parsed.date()).days)

    if age_days <= 7:
        return 0.2, ["published within 7 days"]
    if age_days <= 30:
        return 0.12, ["published within 30 days"]
    return 0.02, ["older but still dated"]


def score_source(query: str, source: SourceRecord, preferred_domains: tuple[str, ...] = ()) -> RankedSource:
    """Score one normalized source against the query intent."""

    score = 0.2 if source.url else 0.0
    reasons: list[str] = []
    domain_score, domain_reasons = _domain_bonus(source.url, preferred_domains)
    text_score, text_reasons = _text_bonus(query, source)
    date_score, date_reasons = _date_bonus(source.published_at)

    score += domain_score + text_score + date_score
    reasons.extend(domain_reasons)
    reasons.extend(text_reasons)
    reasons.extend(date_reasons)

    if source.provider:
        reasons.append(f"provider=`{source.provider}`")
    return RankedSource(source=source, score=score, reasons=tuple(reasons))


def rank_sources(query: str, raw_sources: list[dict | SourceRecord], preferred_domains: tuple[str, ...] = ()) -> list[RankedSource]:
    """Normalize, score, and sort a source list for answer synthesis."""

    ranked = [score_source(query, source, preferred_domains) for source in normalize_sources(raw_sources)]
    return sorted(ranked, key=lambda item: item.score, reverse=True)
