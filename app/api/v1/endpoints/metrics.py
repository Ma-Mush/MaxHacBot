"""Universal metrics ingestion and metadata endpoints."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_api_key
from app.models.metric import MetricRecord
from app.schemas.metric import (
    MetricBatchCreate,
    MetricBatchResponse,
    MetricCreate,
    MetricMetaResponse,
    MetricResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest single metric",
    dependencies=[Depends(verify_api_key)],
)
async def ingest_metric(
    payload: MetricCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single numerical metric record with arbitrary key-value tags."""
    record = MetricRecord(
        name=payload.name,
        value=payload.value,
        unit=payload.unit,
        timestamp=payload.timestamp,
        tags=payload.tags or {},
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.post(
    "/batch",
    response_model=MetricBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest batch metrics (up to 5,000)",
    dependencies=[Depends(verify_api_key)],
)
async def ingest_metrics_batch(
    payload: MetricBatchCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest up to 5,000 metrics in a single bulk transaction."""
    records = [
        MetricRecord(
            name=m.name,
            value=m.value,
            unit=m.unit,
            timestamp=m.timestamp,
            tags=m.tags or {},
        )
        for m in payload.metrics
    ]
    db.add_all(records)
    await db.commit()
    return MetricBatchResponse(
        inserted=len(records),
        status="success",
        message=f"Successfully ingested {len(records)} metric records.",
    )


@router.post(
    "/upload-csv",
    summary="Upload and ingest CSV or Excel (.xlsx) file",
    dependencies=[Depends(verify_api_key)],
)
async def upload_metrics_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and parse an external CSV or Excel file containing sales or metric data."""
    from app.services.csv_importer import csv_importer
    contents = await file.read()
    res = await csv_importer.import_data(contents, file.filename or "uploaded_data.csv", session=db)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to parse file."))
    return res


@router.get(
    "/meta",
    response_model=MetricMetaResponse,
    summary="Get distinct metric names and tag keys in DB",
    dependencies=[Depends(verify_api_key)],
)
async def get_metrics_metadata(
    db: AsyncSession = Depends(get_db),
):
    """Inspect the database to discover all active metric names and dimensional tag keys."""
    # Distinct metric names
    names_result = await db.execute(
        select(distinct(MetricRecord.name)).order_by(MetricRecord.name)
    )
    metric_names = [row[0] for row in names_result.all() if row[0] is not None]

    # Total record count
    count_result = await db.execute(select(func.count(MetricRecord.id)))
    total_records = count_result.scalar_one_or_none() or 0

    # Discover tag keys (compatible with both PostgreSQL jsonb and SQLite json)
    # Query a sample of recent rows to collect keys safely across DB engines
    sample_result = await db.execute(
        select(MetricRecord.tags)
        .order_by(MetricRecord.timestamp.desc())
        .limit(1000)
    )
    tag_keys_set = set()
    for row in sample_result.all():
        tags = row[0]
        if isinstance(tags, dict):
            tag_keys_set.update(tags.keys())

    return MetricMetaResponse(
        metric_names=metric_names,
        tag_keys=sorted(list(tag_keys_set)),
        total_records=total_records,
    )


@router.get(
    "",
    response_model=List[MetricResponse],
    summary="Query metric records",
    dependencies=[Depends(verify_api_key)],
)
async def list_metrics(
    name: Optional[str] = Query(None, description="Filter by metric name"),
    start_date: Optional[datetime] = Query(None, description="Filter records >= start_date"),
    end_date: Optional[datetime] = Query(None, description="Filter records <= end_date"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records offset"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve raw metric records with optional name and date filtering."""
    query = select(MetricRecord).order_by(MetricRecord.timestamp.desc())
    if name:
        query = query.where(MetricRecord.name == name.strip().lower())
    if start_date:
        query = query.where(MetricRecord.timestamp >= start_date)
    if end_date:
        query = query.where(MetricRecord.timestamp <= end_date)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
