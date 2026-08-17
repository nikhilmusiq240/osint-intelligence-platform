from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ConnectorResult:
    connector_name: str
    query: str
    entities: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "success"


class ConnectorProtocol(Protocol):
    name: str
    category: str
    description: str

    def execute(self, query: str, **kwargs: Any) -> ConnectorResult: ...


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, ConnectorProtocol] = {}

    def register_connector(self, connector: ConnectorProtocol) -> None:
        self._connectors[connector.name] = connector

    def unregister_connector(self, name: str) -> None:
        self._connectors.pop(name, None)

    def get_connector(self, name: str) -> ConnectorProtocol:
        if name not in self._connectors:
            raise KeyError(f"Connector '{name}' is not registered.")
        return self._connectors[name]

    def list_connectors(self) -> list[dict[str, str]]:
        return [
            {
                "name": connector.name,
                "category": connector.category,
                "description": connector.description,
            }
            for connector in self._connectors.values()
        ]

    def run(self, connector_name: str, query: str, **kwargs: Any) -> ConnectorResult:
        connector = self.get_connector(connector_name)
        return connector.execute(query=query, **kwargs)


registry = ConnectorRegistry()
