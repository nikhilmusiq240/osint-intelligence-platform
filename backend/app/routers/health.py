from fastapi import APIRouter

from app.config import get_settings
from app.db import check_database_connection
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )


@router.get("/ready", response_model=HealthResponse)
def readiness() -> HealthResponse:
    settings = get_settings()
    database_ok = check_database_connection()
    readiness_status = "ok" if database_ok else "degraded"
    return HealthResponse(
        status=readiness_status,
        service=settings.app_name,
        environment=settings.environment,
    )
