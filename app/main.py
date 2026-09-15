"""Main FastAPI application for OmniMetrics Hub."""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.reports.registry import report_registry

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("omni_metrics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database initialization and plugin discovery."""
    logger.info("Initializing OmniMetrics Hub database...")
    await init_db()

    logger.info("Discovering report plugins...")
    report_registry.discover()
    logger.info(f"Loaded {len(report_registry.list_reports())} report plugins.")

    yield

    logger.info("Shutting down OmniMetrics Hub...")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Self-hosted, extensible business metrics hub & automated reporting engine.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for external dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root Status")
async def root():
    """System welcome and operational metadata."""
    return JSONResponse({
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "registered_reports": [r.to_info_dict() for r in report_registry.list_reports()],
    })
