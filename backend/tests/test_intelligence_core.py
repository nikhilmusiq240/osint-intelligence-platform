from __future__ import annotations

from datetime import datetime, timedelta, timezone

from alembic.config import Config
from fastapi.testclient import TestClient

from alembic import command
from app.db import SessionLocal
from app.main import app
from app.services.connector_registry import registry
from app.services.connector_sdk import NullConnector
from app.services.intelligence_service import InvestigationService

client = TestClient(app)


def test_investigation_service_persists_targets_evidence_and_relationships() -> None:
    session = SessionLocal()
    try:
        service = InvestigationService(session)

        investigation = service.create_investigation(
            "Dark web watchlist", "Monitor suspicious infrastructure."
        )
        target = service.register_target(
            investigation.id, "domain", "example.com", notes="Primary target"
        )
        provenance = service.create_provenance(
            source_name="example-source",
            source_type="web",
            source_url="https://example.com",
            retrieved_at=None,
            metadata={"method": "manual"},
        )

        evidence = service.add_evidence(
            investigation_id=investigation.id,
            target_id=target.id,
            source_name="example-source",
            source_url="https://example.com",
            title="Example record",
            content="Publicly observed reference",
            provenance_id=provenance.id,
        )

        source_entity = service.create_entity(
            investigation_id=investigation.id,
            entity_type="domain",
            value="example.com",
            normalized_value="example.com",
            target_id=target.id,
            provenance_id=provenance.id,
            confidence=0.9,
        )
        target_entity = service.create_entity(
            investigation_id=investigation.id,
            entity_type="email",
            value="admin@example.com",
            normalized_value="admin@example.com",
            target_id=target.id,
            provenance_id=provenance.id,
            confidence=0.7,
        )
        relationship = service.create_relationship(
            investigation_id=investigation.id,
            source_entity_id=source_entity.id,
            target_entity_id=target_entity.id,
            relation_type="related_to",
            confidence=0.82,
            provenance_id=provenance.id,
        )

        assert evidence.investigation_id == investigation.id
        assert evidence.provenance_id == provenance.id
        assert relationship.relation_type == "related_to"
        assert source_entity.normalized_value == "example.com"
        assert service.get_graph(investigation.id)["entities"][0]["value"] in {
            "example.com",
            "admin@example.com",
        }
    finally:
        session.close()


def test_connector_run_lifecycle_tracks_status_changes() -> None:
    session = SessionLocal()
    try:
        service = InvestigationService(session)
        investigation = service.create_investigation(
            "Connector run lifecycle", "Track runtime state."
        )
        target = service.register_target(investigation.id, "domain", "malware.example")

        run = service.create_connector_run(
            investigation_id=investigation.id,
            target_id=target.id,
            connector_name="null",
            query="malware.example",
            metadata={"test": True},
        )
        service.update_connector_run(run.id, status="running", attempts=1)
        service.update_connector_run(
            run.id, status="completed", attempts=1, result_summary={"status": "skipped"}
        )

        refreshed = session.get(type(run), run.id)
        assert refreshed is not None
        assert refreshed.status == "completed"
        assert refreshed.result_summary["status"] == "skipped"
    finally:
        session.close()


def test_connector_execution_persists_results_for_investigation() -> None:
    registry.register_connector(NullConnector())
    session = SessionLocal()
    try:
        service = InvestigationService(session)
        investigation = service.create_investigation(
            "Connector execution", "Ensure registry-backed runs persist."
        )
        target = service.register_target(investigation.id, "domain", "example.net")

        run = service.execute_connector_job(
            investigation_id=investigation.id,
            target_id=target.id,
            connector_name="null",
            query="example.net",
            metadata={"source": "unit-test"},
        )

        assert run.status == "completed"
        assert run.result_summary["status"] == "skipped"
        assert run.connector_name == "null"
    finally:
        session.close()


def test_investigation_graph_api_returns_edges_and_entities() -> None:
    response = client.post(
        "/api/v1/investigations",
        json={
            "title": "Graph API",
            "description": "Check graph endpoint",
            "status": "active",
        },
    )
    investigation = response.json()
    investigation_id = investigation["id"]

    client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={"target_type": "domain", "value": "example.org", "notes": "Graph target"},
    )

    entity_1 = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "target_id": 1,
            "entity_type": "domain",
            "value": "example.org",
            "normalized_value": "example.org",
            "confidence": 0.99,
            "attributes": {"source": "api"},
        },
    ).json()
    entity_2 = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "target_id": 1,
            "entity_type": "email",
            "value": "contact@example.org",
            "normalized_value": "contact@example.org",
            "confidence": 0.7,
            "attributes": {"source": "api"},
        },
    ).json()

    client.post(
        f"/api/v1/investigations/{investigation_id}/relationships",
        json={
            "source_entity_id": entity_1["id"],
            "target_entity_id": entity_2["id"],
            "relation_type": "related_to",
            "confidence": 0.8,
            "attributes": {"source": "api"},
        },
    )

    graph_response = client.get(f"/api/v1/investigations/{investigation_id}/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    assert graph["investigation_id"] == investigation_id
    assert len(graph["entities"]) >= 2
    assert len(graph["relationships"]) >= 1


def test_investigation_lifecycle_tracks_raw_evidence_and_graph_findings() -> None:
    session = SessionLocal()
    try:
        service = InvestigationService(session)
        investigation = service.create_investigation(
            "Lifecycle validation", "Verify full evidence chain."
        )
        target = service.register_target(
            investigation.id, "domain", "example.net", notes="Primary target"
        )
        run = service.create_connector_run(
            investigation_id=investigation.id,
            target_id=target.id,
            connector_name="example-connector",
            query="example.net",
            metadata={
                "connector": {"identity": "example-connector", "version": "1.3.0"}
            },
        )
        provenance = service.create_provenance(
            source_name="example-connector",
            source_type="connector",
            source_url="https://example.net/raw",
            retrieved_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            metadata={
                "connector_identity": "example-connector",
                "connector_version": "1.3.0",
            },
        )
        observed_at = datetime.now(timezone.utc) - timedelta(minutes=2)
        retrieved_at = datetime.now(timezone.utc)
        raw_payload = {
            "status": "ok",
            "source": "https://example.net/raw",
            "response": {"ip": "93.184.216.34"},
        }

        evidence = service.add_evidence(
            investigation_id=investigation.id,
            target_id=target.id,
            source_name="example-connector",
            source_url="https://example.net/raw",
            title="Raw host metadata",
            content="93.184.216.34",
            content_type="application/json",
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            connector_name="example-connector",
            connector_version="1.3.0",
            raw_source_data=raw_payload,
            provenance_id=provenance.id,
            hash_value="abc123",
        )

        entity = service.create_entity(
            investigation_id=investigation.id,
            entity_type="ip_address",
            value="93.184.216.34",
            normalized_value="93.184.216.34",
            confidence=0.97,
            target_id=target.id,
            provenance_id=provenance.id,
            attributes={"source": "connector"},
        )
        relationship = service.create_relationship(
            investigation_id=investigation.id,
            source_entity_id=entity.id,
            target_entity_id=entity.id,
            relation_type="self_reference",
            confidence=1.0,
            provenance_id=provenance.id,
            attributes={"note": "normalized mapping"},
        )

        findings = service.get_investigation_findings(investigation.id)
        assert findings["investigation_id"] == investigation.id
        assert len(findings["evidence"]) == 1
        assert findings["evidence"][0]["connector_name"] == "example-connector"
        assert (
            findings["evidence"][0]["raw_source_data"]["response"]["ip"]
            == "93.184.216.34"
        )
        assert findings["entities"][0]["value"] == "93.184.216.34"
        assert findings["relationships"][0]["relation_type"] == "self_reference"
        assert evidence.raw_source_data["response"]["ip"] == "93.184.216.34"
        assert evidence.connector_name == "example-connector"
        assert evidence.connector_version == "1.3.0"
        assert evidence.is_immutable is True
        assert run.run_metadata["connector"]["version"] == "1.3.0"
        assert relationship.source_entity_id == entity.id
        assert relationship.target_entity_id == entity.id
    finally:
        session.close()


def test_alembic_upgrade_head_on_fresh_sqlite_database(tmp_path) -> None:
    from sqlalchemy import create_engine, inspect

    db_path = tmp_path / "upgrade-head.sqlite"
    db_url = f"sqlite:///{db_path}"

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "alembic")
    cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(cfg, "head")

    # Verify the database file was created by connecting to it
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    engine.dispose()

    # Verify all core tables exist
    expected_tables = {
        "alembic_version",
        "connectors",
        "connector_runs",
        "entities",
        "entity_relationships",
        "evidence",
        "investigation_jobs",
        "investigation_targets",
        "investigations",
        "provenance_records",
    }
    assert tables == expected_tables, f"Expected tables {expected_tables}, got {tables}"
    assert db_path.exists()
