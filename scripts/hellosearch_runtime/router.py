from __future__ import annotations

from pathlib import Path

from .adapters import ClaudeCodeNativeAdapter, CodexNativeAdapter, NoWebAdapter, OpenClawNativeAdapter, RuntimeAdapter
from .models import CapabilityStatus, DetectionReport, HostKind, HostRuntime, RouteDecision


def _adapter_for_runtime(runtime: HostRuntime) -> RuntimeAdapter:
    mapping = {
        HostKind.CODEX: CodexNativeAdapter,
        HostKind.CLAUDE_CODE: ClaudeCodeNativeAdapter,
        HostKind.OPENCLAW: OpenClawNativeAdapter,
    }
    adapter_cls = mapping.get(runtime.host)
    if adapter_cls is None:
        return NoWebAdapter(runtime)
    return adapter_cls(runtime)


def build_adapters(report: DetectionReport) -> list[RuntimeAdapter]:
    """Build adapter descriptors ordered by runtime confidence."""

    adapters = [_adapter_for_runtime(runtime) for runtime in report.runtimes]
    if not adapters:
        adapters.append(
            NoWebAdapter(
                HostRuntime(
                    host=HostKind.UNKNOWN,
                    workspace_root=Path(report.workspace_root),
                )
            )
        )
    return adapters


def choose_route(report: DetectionReport, needs_fetch: bool = False) -> RouteDecision:
    """Choose the best host-native route that is not explicitly blocked."""

    for adapter in build_adapters(report):
        if adapter.is_search_blocked():
            continue
        if needs_fetch and adapter.is_fetch_blocked():
            continue
        if adapter.capabilities.search in (CapabilityStatus.AVAILABLE, CapabilityStatus.UNKNOWN):
            return adapter.build_decision(needs_fetch=needs_fetch)

    runtime = report.primary_runtime or HostRuntime(host=HostKind.UNKNOWN, workspace_root=Path(report.workspace_root))
    return NoWebAdapter(runtime).build_decision(needs_fetch=needs_fetch)
