from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import create_db_tables
from app.logging_config import configure_logging
from app.routers.connectors import router as connectors_router
from app.routers.health import router as health_router
from app.routers.investigations import router as investigations_router
from app.routers.jobs import router as jobs_router
from app.services.connector_registry import registry
from app.services.connector_sdk import NullConnector

configure_logging()
settings = get_settings()


def initialize_runtime_state() -> None:
    create_db_tables()
    if not any(connector.name == "null" for connector in registry._connectors.values()):
        registry.register_connector(NullConnector())


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_runtime_state()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-first OSINT intelligence platform foundation",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(investigations_router, prefix=settings.api_prefix)
app.include_router(jobs_router, prefix=settings.api_prefix)
app.include_router(connectors_router, prefix=settings.api_prefix)

initialize_runtime_state()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}
