from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConnectorContext:
    investigation_id: int | None = None
    job_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConnectorResult:
    connector_name: str
    query: str
    entities: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "success"
    connector_version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    name: str = "base"
    version: str = "1.0.0"
    category: str = "generic"
    description: str = "Base connector implementation."

    def __init__(self, *, context: ConnectorContext | None = None) -> None:
        self.context = context or ConnectorContext()

    @abstractmethod
    def execute(self, query: str, **kwargs: Any) -> ConnectorResult:
        """Execute a connector run for the supplied query."""


class NullConnector(BaseConnector):
    name = "null"
    category = "utility"
    description = (
        "A no-op connector used for testing and safe placeholder registration."
    )

    def execute(self, query: str, **kwargs: Any) -> ConnectorResult:
        return ConnectorResult(
            connector_name=self.name,
            query=query,
            entities=[],
            evidence=[],
            warnings=["No implementation registered for this connector."],
            status="skipped",
            connector_version=self.version,
        )
