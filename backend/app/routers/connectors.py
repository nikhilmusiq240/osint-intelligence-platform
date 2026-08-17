from fastapi import APIRouter, HTTPException, status

from app.schemas import ConnectorInfo
from app.services.connector_registry import registry

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("", response_model=list[ConnectorInfo])
def list_connectors() -> list[ConnectorInfo]:
    return [ConnectorInfo(**item) for item in registry.list_connectors()]


@router.get("/{connector_name}", response_model=ConnectorInfo)
def get_connector(connector_name: str) -> ConnectorInfo:
    try:
        connector = registry.get_connector(connector_name)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return ConnectorInfo(
        name=connector.name,
        category=connector.category,
        description=connector.description,
    )
