from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.connector_sdk import ConnectorContext, NullConnector


def test_settings_values_are_loaded() -> None:
    settings = get_settings()
    assert settings.app_name == "osint-intelligence-platform"
    assert settings.api_prefix == "/api/v1"
    assert settings.database_url.startswith(("sqlite", "postgresql+"))


def test_health_and_readiness_routes() -> None:
    client = TestClient(app)

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    readiness = client.get("/api/v1/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["service"] == "osint-intelligence-platform"


def test_connector_sdk_placeholder_behavior() -> None:
    connector = NullConnector(context=ConnectorContext(investigation_id=1, job_id=7))
    result = connector.execute("example query")

    assert result.connector_name == "null"
    assert result.status == "skipped"
    assert result.warnings
    assert result.entities == []
    assert result.evidence == []


def test_root_endpoint_status() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "osint-intelligence-platform"
