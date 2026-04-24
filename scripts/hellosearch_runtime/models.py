from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class HostKind(str, Enum):
    CODEX = "codex"
    CLAUDE_CODE = "claude-code"
    OPENCLAW = "openclaw"
    UNKNOWN = "unknown"


class BackendKind(str, Enum):
    HOST_NATIVE = "host_native"
    NONE = "none"


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DetectionSignal:
    """Single piece of evidence used to infer the active host runtime."""

    kind: str
    detail: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HostCapabilities:
    """Normalized capability view for a runtime or adapter."""

    search: CapabilityStatus = CapabilityStatus.UNKNOWN
    fetch: CapabilityStatus = CapabilityStatus.UNKNOWN
    open_page: CapabilityStatus = CapabilityStatus.UNKNOWN
    map_site: CapabilityStatus = CapabilityStatus.UNKNOWN

    def to_dict(self) -> dict[str, str]:
        return {
            "search": self.search.value,
            "fetch": self.fetch.value,
            "open_page": self.open_page.value,
            "map_site": self.map_site.value,
        }


@dataclass(frozen=True)
class HostRuntime:
    """Best-effort detection result for one host family."""

    host: HostKind
    workspace_root: Path
    signals: tuple[DetectionSignal, ...] = ()
    capabilities: HostCapabilities = field(default_factory=HostCapabilities)
    notes: tuple[str, ...] = ()

    @property
    def confidence(self) -> float:
        if not self.signals:
            return 0.0
        return round(sum(signal.confidence for signal in self.signals), 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host.value,
            "workspace_root": str(self.workspace_root),
            "confidence": self.confidence,
            "signals": [signal.to_dict() for signal in self.signals],
            "capabilities": self.capabilities.to_dict(),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class DetectionReport:
    """Detection summary for all candidate runtimes in the current environment."""

    workspace_root: Path
    runtimes: tuple[HostRuntime, ...]
    primary_runtime: HostRuntime | None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_root": str(self.workspace_root),
            "primary_runtime": self.primary_runtime.to_dict() if self.primary_runtime else None,
            "runtimes": [runtime.to_dict() for runtime in self.runtimes],
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class RouteDecision:
    """Routing recommendation for the next search workflow step."""

    adapter_id: str
    host: HostKind
    backend: BackendKind
    capabilities: HostCapabilities
    reason: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "host": self.host.value,
            "backend": self.backend.value,
            "capabilities": self.capabilities.to_dict(),
            "reason": self.reason,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class SourceRecord:
    """Normalized source entry shared by all backends."""

    title: str = ""
    url: str = ""
    snippet: str = ""
    provider: str = ""
    published_at: str = ""
    retrieved_at: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SearchResponse:
    """Normalized search response shape for future adapters."""

    content: str
    sources: tuple[SourceRecord, ...] = ()
    raw: Any = None


@dataclass(frozen=True)
class FetchResponse:
    """Normalized fetch response shape for future adapters."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any = None
