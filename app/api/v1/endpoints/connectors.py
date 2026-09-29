"""Marketplace and external systems connectors API endpoints."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_api_key
from app.connectors.ozon import OzonConnector, ozon_connector
from app.connectors.wildberries import WildberriesConnector, wb_connector

router = APIRouter()


@router.post(
    "/wildberries/sync",
    summary="Synchronize sales & orders from Wildberries API",
    dependencies=[Depends(verify_api_key)],
)
async def sync_wildberries(
    days: int = Query(7, ge=1, le=90, description="Number of past days to sync"),
    mock: bool = Query(False, description="Force simulated sandbox data for demo"),
    api_key: Optional[str] = Query(None, description="Optional override for WB API key"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Pull sales telemetry from Wildberries Statistics API and ingest into metrics database."""
    connector = WildberriesConnector(api_key=api_key) if api_key else wb_connector
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    res = await connector.fetch_and_ingest(
        start_date=start_date,
        end_date=end_date,
        session=db,
        force_mock=mock,
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("message", "Wildberries sync failed."),
        )
    return res


@router.get(
    "/wildberries/status",
    summary="Test Wildberries API connection",
    dependencies=[Depends(verify_api_key)],
)
async def test_wildberries_status() -> Dict[str, Any]:
    """Check connectivity to Wildberries Statistics API with configured WB_API_KEY."""
    return await wb_connector.test_connection()


@router.post(
    "/ozon/sync",
    summary="Synchronize postings & revenue from Ozon Seller API",
    dependencies=[Depends(verify_api_key)],
)
async def sync_ozon(
    days: int = Query(7, ge=1, le=90, description="Number of past days to sync"),
    mock: bool = Query(False, description="Force simulated sandbox data for demo"),
    client_id: Optional[str] = Query(None, description="Optional override for Ozon Client ID"),
    api_key: Optional[str] = Query(None, description="Optional override for Ozon API Key"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Pull postings and financial metrics from Ozon Seller API and ingest into metrics database."""
    connector = OzonConnector(client_id=client_id, api_key=api_key) if (client_id and api_key) else ozon_connector
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    res = await connector.fetch_and_ingest(
        start_date=start_date,
        end_date=end_date,
        session=db,
        force_mock=mock,
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("message", "Ozon sync failed."),
        )
    return res


@router.get(
    "/ozon/status",
    summary="Test Ozon Seller API connection",
    dependencies=[Depends(verify_api_key)],
)
async def test_ozon_status() -> Dict[str, Any]:
    """Check connectivity to Ozon Seller API with configured credentials."""
    return await ozon_connector.test_connection()

