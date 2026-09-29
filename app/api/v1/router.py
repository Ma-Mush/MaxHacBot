"""API v1 router aggregating all endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import connectors, health, max_webhook, metrics, reports

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(max_webhook.router, prefix="/max/webhook", tags=["MAX Messenger"])
api_router.include_router(connectors.router, prefix="/connectors", tags=["Connectors & Marketplaces"])

