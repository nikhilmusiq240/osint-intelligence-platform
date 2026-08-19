from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.services.connector_registry import registry
from app.services.connector_sdk import BaseConnector, ConnectorResult


class SyntheticConnector(BaseConnector):
    name = "synthetic-test"
    category = "test"
    description = "Synthetic connector used to verify connector execution."

    def execute(self, query: str, **kwargs) -> ConnectorResult:
        return ConnectorResult(
            connector_name=self.name,
            query=query,
            entities=[
                {
                    "entity_type": "domain",
                    "value": query,
                    "normalized_value": query.lower(),
                    "confidence": 0.95,
                    "attributes": {"source": "synthetic-test"},
                    "is_observed": True,
                }
            ],
            evidence=[
                {
                    "source_name": "synthetic-test",
                    "source_url": f"https://{query}",
                    "title": "Synthetic observation",
                    "content": f"Observed public reference for {query}",
                    "content_type": "text",
                    "observed_at": datetime.now(timezone.utc),
                    "retrieved_at": datetime.now(timezone.utc),
                    "raw_source_data": {
                        "query": query,
                        "synthetic": True,
                    },
                }
            ],
            warnings=[],
            status="success",
        )


client = TestClient(app)


def test_connector_execution_api_persists_entities_evidence_and_provenance() -> None:
    registry.register_connector(SyntheticConnector())

    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Synthetic connector API test",
            "description": "Verify complete connector execution lifecycle.",
            "status": "active",
        },
    ).json()

    investigation_id = investigation["id"]

    target = client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={
            "target_type": "domain",
            "value": "example.net",
            "normalized_value": "example.net",
        },
    ).json()

    target_id = target["id"]

    run_response = client.post(
        f"/api/v1/investigations/{investigation_id}/connector-runs",
        json={
            "connector_name": "synthetic-test",
            "query": "example.net",
            "target_id": target_id,
            "metadata": {"test": True},
        },
    )

    assert run_response.status_code == 201
    run = run_response.json()
    assert run["status"] == "queued"

    execute_response = client.post(
        f"/api/v1/investigations/{investigation_id}/connector-runs/{run['id']}/execute"
    )

    assert execute_response.status_code == 200

    executed = execute_response.json()

    assert executed["status"] == "completed"
    assert executed["started_at"] is not None
    assert executed["completed_at"] is not None
    assert executed["attempts"] == 1
    assert executed["result_summary"]["entity_count"] == 1
    assert executed["result_summary"]["evidence_count"] == 1
    assert executed["result_summary"]["provenance_id"] is not None

    entities = client.get(f"/api/v1/investigations/{investigation_id}/entities").json()

    evidence = client.get(f"/api/v1/investigations/{investigation_id}/evidence").json()

    assert len(entities) == 1
    assert entities[0]["value"] == "example.net"
    assert entities[0]["target_id"] == target_id
    assert entities[0]["provenance_id"] == executed["result_summary"]["provenance_id"]

    assert len(evidence) == 1
    assert evidence[0]["source_name"] == "synthetic-test"
    assert evidence[0]["target_id"] == target_id
    assert evidence[0]["provenance_id"] == executed["result_summary"]["provenance_id"]
    assert evidence[0]["raw_source_data"]["synthetic"] is True


def test_connector_execution_api_rejects_wrong_investigation_run() -> None:
    registry.register_connector(SyntheticConnector())

    first = client.post(
        "/api/v1/investigations",
        json={
            "title": "First investigation",
            "description": "Execution ownership test.",
            "status": "active",
        },
    ).json()

    second = client.post(
        "/api/v1/investigations",
        json={
            "title": "Second investigation",
            "description": "Execution ownership test.",
            "status": "active",
        },
    ).json()

    run = client.post(
        f"/api/v1/investigations/{first['id']}/connector-runs",
        json={
            "connector_name": "synthetic-test",
            "query": "example.net",
        },
    ).json()

    response = client.post(
        f"/api/v1/investigations/{second['id']}/connector-runs/{run['id']}/execute"
    )

    assert response.status_code == 404


def test_connector_execution_api_rejects_missing_investigation() -> None:
    response = client.post(
        "/api/v1/investigations/999999/connector-runs/999999/execute"
    )

    assert response.status_code == 404
