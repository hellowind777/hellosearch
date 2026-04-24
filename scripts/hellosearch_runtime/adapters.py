from __future__ import annotations

from abc import ABC
from pathlib import Path

from .models import BackendKind, CapabilityStatus, HostCapabilities, HostKind, HostRuntime, RouteDecision


class RuntimeAdapter(ABC):
    """Base adapter descriptor for a host-native search backend."""

    adapter_id = "runtime"
    backend = BackendKind.HOST_NATIVE

    def __init__(self, runtime: HostRuntime):
        self.runtime = runtime

    @property
    def host(self) -> HostKind:
        return self.runtime.host

    @property
    def capabilities(self) -> HostCapabilities:
        return self.runtime.capabilities

    def is_search_blocked(self) -> bool:
        return self.capabilities.search is CapabilityStatus.UNAVAILABLE

    def is_fetch_blocked(self) -> bool:
        return self.capabilities.fetch is CapabilityStatus.UNAVAILABLE

    def build_decision(self, needs_fetch: bool = False) -> RouteDecision:
        """Return a normalized routing decision for this adapter."""

        return RouteDecision(
            adapter_id=self.adapter_id,
            host=self.host,
            backend=self.backend,
            capabilities=self.capabilities,
            reason=self.reason(needs_fetch=needs_fetch),
            notes=self.runtime.notes,
        )

    def reason(self, needs_fetch: bool = False) -> str:
        requirement = "search + fetch" if needs_fetch else "search"
        return f"Prefer {self.host.value} host-native {requirement} when the current session exposes it."

    def search(self, *args, **kwargs):
        """Raise until a concrete host integration is implemented."""

        raise NotImplementedError(
            f"{self.adapter_id} is a routing descriptor. Implement concrete host invocation before calling `search`."
        )

    def fetch(self, *args, **kwargs):
        """Raise until a concrete host integration is implemented."""

        raise NotImplementedError(
            f"{self.adapter_id} is a routing descriptor. Implement concrete host invocation before calling `fetch`."
        )


class CodexNativeAdapter(RuntimeAdapter):
    adapter_id = "codex-native"

    def reason(self, needs_fetch: bool = False) -> str:
        if needs_fetch:
            return "Prefer Codex native web search and page-open or fetch tools for this skill."
        return "Prefer Codex native web search for this skill."


class ClaudeCodeNativeAdapter(RuntimeAdapter):
    adapter_id = "claude-code-native"

    def reason(self, needs_fetch: bool = False) -> str:
        if needs_fetch:
            return "Prefer Claude Code native web tools when the workspace has not disabled WebSearch or WebFetch."
        return "Prefer Claude Code native WebSearch when the workspace has not disabled it."


class OpenClawNativeAdapter(RuntimeAdapter):
    adapter_id = "openclaw-native"

    def reason(self, needs_fetch: bool = False) -> str:
        if needs_fetch:
            return "Prefer the active OpenClaw native web provider for search and fetch in this skill."
        return "Prefer the active OpenClaw native web provider in this skill."


class NoWebAdapter(RuntimeAdapter):
    adapter_id = "no-web"
    backend = BackendKind.NONE

    def __init__(self, runtime: HostRuntime | None = None):
        runtime = runtime or HostRuntime(
            host=HostKind.UNKNOWN,
            workspace_root=Path.cwd(),
        )
        super().__init__(runtime)

    @property
    def capabilities(self) -> HostCapabilities:
        return HostCapabilities(
            search=CapabilityStatus.UNAVAILABLE,
            fetch=CapabilityStatus.UNAVAILABLE,
            open_page=CapabilityStatus.UNAVAILABLE,
            map_site=CapabilityStatus.UNAVAILABLE,
        )

    def reason(self, needs_fetch: bool = False) -> str:
        if needs_fetch:
            return "No confirmed live web search and fetch path is available in the current environment."
        return "No confirmed live web search path is available in the current environment."
