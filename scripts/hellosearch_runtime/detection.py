from __future__ import annotations

import json
import shutil
from pathlib import Path
import tomllib

from .models import (
    CapabilityStatus,
    DetectionReport,
    DetectionSignal,
    HostCapabilities,
    HostKind,
    HostRuntime,
)


def locate_workspace_root(start: Path | None = None) -> Path:
    """Return the nearest workspace root-like directory for the current path."""

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
        if (candidate / ".claude").exists():
            return candidate
    return current


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _load_claude_code_settings(workspace_root: Path) -> dict:
    settings_path = workspace_root / ".claude" / "settings.json"
    if not settings_path.exists():
        return {}
    try:
        return json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_codex_config() -> dict:
    config_path = Path.home() / ".codex" / "config.toml"
    if not config_path.exists():
        return {}
    try:
        return tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _detect_codex(workspace_root: Path) -> HostRuntime | None:
    signals: list[DetectionSignal] = []
    if _command_exists("codex"):
        signals.append(DetectionSignal("command", "Found `codex` in PATH", 0.8))
    if (Path.home() / ".codex").exists():
        signals.append(DetectionSignal("home", "Found `~/.codex`", 0.7))
    if not signals:
        return None

    config = _load_codex_config()
    web_search_mode = str(config.get("web_search", "")).lower()
    search_status = CapabilityStatus.AVAILABLE if web_search_mode == "live" else CapabilityStatus.UNKNOWN
    open_page_status = CapabilityStatus.AVAILABLE if web_search_mode == "live" else CapabilityStatus.UNKNOWN
    notes = [
        "Codex native web search depends on the current session enabling live web search.",
        "Treat capability flags as best-effort until the session confirms tool availability.",
    ]
    if web_search_mode:
        signals.append(DetectionSignal("config", f"Codex config web_search={web_search_mode}", 0.9))
        notes.append(f"Loaded Codex config with `web_search={web_search_mode}`.")
    capabilities = HostCapabilities(
        search=search_status,
        fetch=CapabilityStatus.UNKNOWN,
        open_page=open_page_status,
        map_site=CapabilityStatus.UNAVAILABLE,
    )
    return HostRuntime(
        host=HostKind.CODEX,
        workspace_root=workspace_root,
        signals=tuple(signals),
        capabilities=capabilities,
        notes=tuple(notes),
    )


def _detect_claude_code(workspace_root: Path) -> HostRuntime | None:
    signals: list[DetectionSignal] = []
    if _command_exists("claude"):
        signals.append(DetectionSignal("command", "Found `claude` in PATH", 0.8))

    settings_path = workspace_root / ".claude" / "settings.json"
    if settings_path.exists():
        signals.append(DetectionSignal("workspace", f"Found `{settings_path}`", 0.9))

    if not signals:
        return None

    settings = _load_claude_code_settings(workspace_root)
    deny_list = settings.get("permissions", {}).get("deny", [])

    search = CapabilityStatus.UNKNOWN
    fetch = CapabilityStatus.UNKNOWN
    notes: list[str] = [
        "Claude Code native web capability can be restricted per workspace.",
    ]

    if "WebSearch" in deny_list:
        search = CapabilityStatus.UNAVAILABLE
        notes.append("`.claude/settings.json` denies `WebSearch`.")
    if "WebFetch" in deny_list:
        fetch = CapabilityStatus.UNAVAILABLE
        notes.append("`.claude/settings.json` denies `WebFetch`.")

    capabilities = HostCapabilities(
        search=search,
        fetch=fetch,
        open_page=fetch,
        map_site=CapabilityStatus.UNAVAILABLE,
    )
    return HostRuntime(
        host=HostKind.CLAUDE_CODE,
        workspace_root=workspace_root,
        signals=tuple(signals),
        capabilities=capabilities,
        notes=tuple(notes),
    )


def _detect_openclaw(workspace_root: Path) -> HostRuntime | None:
    signals: list[DetectionSignal] = []
    if _command_exists("openclaw"):
        signals.append(DetectionSignal("command", "Found `openclaw` in PATH", 0.8))
    if not signals:
        return None

    capabilities = HostCapabilities(
        search=CapabilityStatus.UNKNOWN,
        fetch=CapabilityStatus.UNKNOWN,
        open_page=CapabilityStatus.UNKNOWN,
        map_site=CapabilityStatus.UNKNOWN,
    )
    notes = (
        "OpenClaw web capability depends on the active provider or attached web tool.",
    )
    return HostRuntime(
        host=HostKind.OPENCLAW,
        workspace_root=workspace_root,
        signals=tuple(signals),
        capabilities=capabilities,
        notes=notes,
    )


def detect_runtime_environment(start: Path | None = None) -> DetectionReport:
    """Detect candidate runtimes and produce a best-effort primary runtime."""

    workspace_root = locate_workspace_root(start)
    candidates = [
        candidate
        for candidate in (
            _detect_codex(workspace_root),
            _detect_claude_code(workspace_root),
            _detect_openclaw(workspace_root),
        )
        if candidate is not None
    ]
    runtimes = tuple(sorted(candidates, key=lambda item: item.confidence, reverse=True))
    primary_runtime = runtimes[0] if runtimes else None

    notes = (
        "Primary runtime selection is heuristic and should not override explicit host context.",
    )
    return DetectionReport(
        workspace_root=workspace_root,
        runtimes=runtimes,
        primary_runtime=primary_runtime,
        notes=notes,
    )
