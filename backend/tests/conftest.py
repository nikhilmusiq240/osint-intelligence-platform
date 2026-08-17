from __future__ import annotations

import os

import pytest

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"


@pytest.fixture(autouse=True)
def reset_test_state() -> None:
    from app.db import Base, engine
    from app.services.connector_registry import registry
    from app.services.connector_sdk import NullConnector

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    registry._connectors.clear()
    registry.register_connector(NullConnector())
    yield
    registry._connectors.clear()
    Base.metadata.drop_all(bind=engine)
