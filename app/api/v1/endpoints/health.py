"""Health check and system status endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.reports.registry import report_registry

router = APIRouter()


@router.get("", summary="Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check API and database health."""
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {str(exc)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
        "registered_reports_count": len(report_registry.list_reports()),
    }
