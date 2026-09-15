"""API v1 router aggregating all endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import health, metrics, reports

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
