from __future__ import annotations

from typing import Any, Protocol

from app.services.connector_sdk import ConnectorResult


class ConnectorProtocol(Protocol):
    name: str
    category: str
    description: str
    version: str

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
