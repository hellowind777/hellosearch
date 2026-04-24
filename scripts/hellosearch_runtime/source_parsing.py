from __future__ import annotations

import ast
import json
import re
from urllib.parse import urlsplit


_RAW_URL_PATTERN = re.compile(r"https?://[^\s<>()\"'`]+")
_MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_SOURCES_HEADING_PATTERN = re.compile(
    r"(?im)^(?:#{1,6}\s*)?(?:\*\*|__)?\s*(sources?|references?|citations?|信源|参考资料|参考|引用|来源列表|来源)\s*(?:\*\*|__)?\s*(?:[:：])?\s*$"
)
_CALL_BLOCK_PATTERN = re.compile(r"(?im)(^|\n)\s*(sources|citations|references)\s*\(")


def split_answer_and_sources(text: str) -> tuple[str, list[dict]]:
    """Split answer text from a trailing citation block when possible."""

    raw = (text or "").strip()
    if not raw:
        return "", []

    for splitter in (_split_call_block, _split_heading_block, _split_tail_link_block):
        answer, sources = splitter(raw)
        if sources:
            return answer, sources
    return raw, []


def extract_sources_from_text(text: str) -> list[dict]:
    """Extract unique source records from Markdown links and raw URLs."""

    seen: set[str] = set()
    sources: list[dict] = []

    for title, url in _MD_LINK_PATTERN.findall(text or ""):
        normalized = _normalize_url(url)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        record = {"url": normalized}
        if title.strip():
            record["title"] = title.strip()
        sources.append(record)

    for match in _RAW_URL_PATTERN.findall(text or ""):
        normalized = _normalize_url(match)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        sources.append({"url": normalized})

    return sources


def merge_raw_sources(*source_lists: list[dict]) -> list[dict]:
    """Merge raw source dictionaries by normalized URL."""

    seen: set[str] = set()
    merged: list[dict] = []
    for sources in source_lists:
        for item in sources or []:
            url = _normalize_url((item or {}).get("url", ""))
            if not url or url in seen:
                continue
            seen.add(url)
            merged.append({**item, "url": url})
    return merged


def parse_source_payload(payload: str) -> list[dict]:
    """Parse JSON- or Python-like citation payloads into raw sources."""

    content = (payload or "").strip().rstrip(";")
    if not content:
        return []

    data = None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(content)
        except (ValueError, SyntaxError):
            return extract_sources_from_text(content)

    if isinstance(data, dict):
        data = data.get("sources", data.get("citations", data.get("references", data)))
    if not isinstance(data, list):
        data = [data]

    raw_sources: list[dict] = []
    for item in data:
        if isinstance(item, str):
            raw_sources.extend(extract_sources_from_text(item))
            continue
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            url = _normalize_url(item[1] or "")
            if not url:
                continue
            record = {"url": url}
            title = item[0]
            if isinstance(title, str) and title.strip():
                record["title"] = title.strip()
            raw_sources.append(record)
            continue
        if isinstance(item, dict):
            url = _normalize_url(item.get("url") or item.get("href") or item.get("link") or "")
            if not url:
                continue
            record = {"url": url}
            for key_in, key_out in (("title", "title"), ("name", "title"), ("label", "title"), ("snippet", "snippet"), ("description", "snippet"), ("provider", "provider")):
                value = item.get(key_in)
                if isinstance(value, str) and value.strip():
                    record[key_out] = value.strip()
            raw_sources.append(record)
    return merge_raw_sources(raw_sources)


def _split_call_block(text: str) -> tuple[str, list[dict]]:
    matches = list(_CALL_BLOCK_PATTERN.finditer(text))
    for match in reversed(matches):
        open_index = match.end() - 1
        extracted = _extract_balanced_call(text, open_index)
        if not extracted:
            continue
        close_index, payload = extracted
        if text[close_index + 1 :].strip():
            continue
        sources = parse_source_payload(payload)
        if sources:
            return text[: match.start()].rstrip(), sources
    return text, []


def _split_heading_block(text: str) -> tuple[str, list[dict]]:
    matches = list(_SOURCES_HEADING_PATTERN.finditer(text))
    for match in reversed(matches):
        block = text[match.start() :]
        sources = extract_sources_from_text(block)
        if sources:
            return text[: match.start()].rstrip(), sources
    return text, []


def _split_tail_link_block(text: str) -> tuple[str, list[dict]]:
    lines = text.splitlines()
    if len(lines) < 2:
        return text, []

    idx = len(lines) - 1
    while idx >= 0 and not lines[idx].strip():
        idx -= 1
    if idx < 0:
        return text, []

    link_lines: list[str] = []
    while idx >= 0:
        line = lines[idx].strip()
        if not line:
            idx -= 1
            continue
        if not (_MD_LINK_PATTERN.search(line) or _RAW_URL_PATTERN.search(line)):
            break
        link_lines.append(lines[idx])
        idx -= 1

    if len(link_lines) < 2:
        return text, []

    link_lines.reverse()
    sources = extract_sources_from_text("\n".join(link_lines))
    if not sources:
        return text, []
    return "\n".join(lines[: idx + 1]).rstrip(), sources


def _extract_balanced_call(text: str, open_index: int) -> tuple[int, str] | None:
    if open_index < 0 or open_index >= len(text) or text[open_index] != "(":
        return None

    depth = 1
    string_char = ""
    escaped = False
    for index in range(open_index + 1, len(text)):
        char = text[index]
        if string_char:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == string_char:
                string_char = ""
            continue

        if char in {"'", '"'}:
            string_char = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index, text[open_index + 1 : index]
    return None


def _normalize_url(url: str) -> str:
    cleaned = (url or "").strip().rstrip(".,;:!?)]}")
    if not cleaned:
        return ""
    parts = urlsplit(cleaned)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    return cleaned
