from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_investigation_crud_flow() -> None:
    create_response = client.post(
        "/api/v1/investigations",
        json={
            "title": "Threat actor review",
            "description": "Review suspicious infrastructure.",
            "status": "active",
        },
    )
    assert create_response.status_code == 201
    investigation = create_response.json()
    assert investigation["title"] == "Threat actor review"
    assert investigation["status"] == "active"

    fetch_response = client.get(f"/api/v1/investigations/{investigation['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["id"] == investigation["id"]


def test_investigation_list() -> None:
    client.post(
        "/api/v1/investigations",
        json={
            "title": "Investigation 1",
            "description": "First investigation",
            "status": "active",
        },
    )
    client.post(
        "/api/v1/investigations",
        json={
            "title": "Investigation 2",
            "description": "Second investigation",
            "status": "draft",
        },
    )

    response = client.get("/api/v1/investigations")
    assert response.status_code == 200
    investigations = response.json()
    assert isinstance(investigations, list)
    assert len(investigations) >= 2
    titles = [inv["title"] for inv in investigations]
    assert "Investigation 1" in titles
    assert "Investigation 2" in titles


def test_investigation_update() -> None:
    create_response = client.post(
        "/api/v1/investigations",
        json={
            "title": "Original title",
            "description": "Original description",
            "status": "draft",
        },
    )
    investigation = create_response.json()
    investigation_id = investigation["id"]

    update_response = client.put(
        f"/api/v1/investigations/{investigation_id}",
        json={
            "title": "Updated title",
            "status": "active",
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Updated title"
    assert updated["status"] == "active"
    assert updated["description"] == "Original description"


def test_investigation_target_crud() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Target test",
            "description": "Test target operations",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    create_target_response = client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={
            "target_type": "domain",
            "value": "example.com",
            "normalized_value": "example.com",
            "notes": "Primary domain",
            "attributes": {"category": "infrastructure"},
        },
    )
    assert create_target_response.status_code == 201
    target = create_target_response.json()
    assert target["value"] == "example.com"
    assert target["target_type"] == "domain"
    target_id = target["id"]

    get_target_response = client.get(
        f"/api/v1/investigations/{investigation_id}/targets/{target_id}"
    )
    assert get_target_response.status_code == 200
    fetched_target = get_target_response.json()
    assert fetched_target["id"] == target_id

    update_target_response = client.put(
        f"/api/v1/investigations/{investigation_id}/targets/{target_id}",
        json={
            "notes": "Updated notes",
            "attributes": {"category": "updated"},
        },
    )
    assert update_target_response.status_code == 200
    updated_target = update_target_response.json()
    assert updated_target["notes"] == "Updated notes"
    assert updated_target["attributes"]["category"] == "updated"


def test_investigation_target_list() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Multiple targets",
            "description": "Test listing targets",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={
            "target_type": "domain",
            "value": "example1.com",
            "normalized_value": "example1.com",
        },
    )
    client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={
            "target_type": "domain",
            "value": "example2.com",
            "normalized_value": "example2.com",
        },
    )

    list_response = client.get(f"/api/v1/investigations/{investigation_id}/targets")
    assert list_response.status_code == 200
    targets = list_response.json()
    assert len(targets) >= 2
    values = [t["value"] for t in targets]
    assert "example1.com" in values
    assert "example2.com" in values


def test_investigation_evidence_crud() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Evidence test",
            "description": "Test evidence operations",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    now = datetime.now(timezone.utc)
    create_evidence_response = client.post(
        f"/api/v1/investigations/{investigation_id}/evidence",
        json={
            "source_name": "test-source",
            "source_url": "https://example.com/evidence",
            "title": "Test evidence item",
            "content": "Evidence content",
            "content_type": "text",
            "observed_at": now.isoformat(),
            "retrieved_at": now.isoformat(),
            "connector_name": "test-connector",
            "raw_source_data": {"key": "value"},
            "is_immutable": True,
        },
    )
    assert create_evidence_response.status_code == 201
    evidence = create_evidence_response.json()
    assert evidence["source_name"] == "test-source"
    assert evidence["title"] == "Test evidence item"

    list_response = client.get(f"/api/v1/investigations/{investigation_id}/evidence")
    assert list_response.status_code == 200
    evidence_list = list_response.json()
    assert len(evidence_list) >= 1
    assert evidence_list[0]["source_name"] == "test-source"


def test_investigation_entity_and_relationship_crud() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Graph test",
            "description": "Test entity and relationship operations",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    entity1_response = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "entity_type": "domain",
            "value": "example.com",
            "normalized_value": "example.com",
            "confidence": 0.95,
            "attributes": {"category": "infrastructure"},
        },
    )
    assert entity1_response.status_code == 201
    entity1 = entity1_response.json()

    entity2_response = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "entity_type": "email",
            "value": "admin@example.com",
            "normalized_value": "admin@example.com",
            "confidence": 0.85,
            "attributes": {"category": "communication"},
        },
    )
    assert entity2_response.status_code == 201
    entity2 = entity2_response.json()

    relationship_response = client.post(
        f"/api/v1/investigations/{investigation_id}/relationships",
        json={
            "source_entity_id": entity1["id"],
            "target_entity_id": entity2["id"],
            "relation_type": "has_email",
            "confidence": 0.9,
            "attributes": {"evidence": "whois"},
        },
    )
    assert relationship_response.status_code == 201
    relationship = relationship_response.json()
    assert relationship["relation_type"] == "has_email"

    entities_response = client.get(
        f"/api/v1/investigations/{investigation_id}/entities"
    )
    assert entities_response.status_code == 200
    entities = entities_response.json()
    assert len(entities) >= 2

    relationships_response = client.get(
        f"/api/v1/investigations/{investigation_id}/relationships"
    )
    assert relationships_response.status_code == 200
    relationships = relationships_response.json()
    assert len(relationships) >= 1


def test_investigation_graph_retrieval() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Graph retrieval test",
            "description": "Test graph endpoint",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    entity1 = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "entity_type": "domain",
            "value": "example.com",
            "normalized_value": "example.com",
            "confidence": 0.95,
        },
    ).json()

    entity2 = client.post(
        f"/api/v1/investigations/{investigation_id}/entities",
        json={
            "entity_type": "ip",
            "value": "192.0.2.1",
            "normalized_value": "192.0.2.1",
            "confidence": 0.9,
        },
    ).json()

    client.post(
        f"/api/v1/investigations/{investigation_id}/relationships",
        json={
            "source_entity_id": entity1["id"],
            "target_entity_id": entity2["id"],
            "relation_type": "resolves_to",
            "confidence": 0.95,
        },
    )

    graph_response = client.get(f"/api/v1/investigations/{investigation_id}/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    assert graph["investigation_id"] == investigation_id
    assert len(graph["entities"]) == 2
    assert len(graph["relationships"]) == 1
    entity_values = [e["value"] for e in graph["entities"]]
    assert "example.com" in entity_values
    assert "192.0.2.1" in entity_values


def test_connector_run_crud() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Connector run test",
            "description": "Test connector runs",
            "status": "active",
        },
    ).json()
    investigation_id = investigation["id"]

    target = client.post(
        f"/api/v1/investigations/{investigation_id}/targets",
        json={
            "target_type": "domain",
            "value": "example.com",
            "normalized_value": "example.com",
        },
    ).json()
    target_id = target["id"]

    create_run_response = client.post(
        f"/api/v1/investigations/{investigation_id}/connector-runs",
        json={
            "connector_name": "null",
            "query": "example.com",
            "target_id": target_id,
            "metadata": {"source": "api-test"},
        },
    )
    assert create_run_response.status_code == 201
    run = create_run_response.json()
    assert run["connector_name"] == "null"
    assert run["query"] == "example.com"
    assert run["status"] == "queued"

    list_response = client.get(
        f"/api/v1/investigations/{investigation_id}/connector-runs"
    )
    assert list_response.status_code == 200
    runs = list_response.json()
    assert len(runs) >= 1
    assert runs[0]["connector_name"] == "null"


def test_job_creation_flow() -> None:
    investigation = client.post(
        "/api/v1/investigations",
        json={
            "title": "Domain collection",
            "description": "Collect domain references",
            "status": "draft",
        },
    ).json()

    response = client.post(
        "/api/v1/jobs",
        json={
            "investigation_id": investigation["id"],
            "connector_name": "null",
            "query": "example.com",
            "job_metadata": {"source": "unit-test"},
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["connector_name"] == "null"
    assert payload["query"] == "example.com"
    assert payload["status"] == "queued"


def test_connector_listing_and_lookup() -> None:
    list_response = client.get("/api/v1/connectors")
    assert list_response.status_code == 200
    connectors = list_response.json()
    assert isinstance(connectors, list)

    lookup_response = client.get("/api/v1/connectors/null")
    assert lookup_response.status_code == 200
    payload = lookup_response.json()
    assert payload["name"] == "null"
    assert payload["category"] == "utility"


def test_investigation_not_found() -> None:
    response = client.get("/api/v1/investigations/9999")
    assert response.status_code == 404


def test_target_not_found() -> None:
    response = client.get("/api/v1/investigations/1/targets/9999")
    assert response.status_code == 404
