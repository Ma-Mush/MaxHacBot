"""Metric schemas for ingestion and query responses."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class MetricCreate(BaseModel):
    """Payload for creating a single metric."""
    name: str = Field(..., min_length=1, max_length=255, description="Metric name, e.g. revenue, active_users")
    value: float = Field(..., description="Numerical metric value")
    unit: Optional[str] = Field(None, max_length=64, description="Unit, e.g. USD, ms, %, pcs")
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp in UTC. Defaults to current time."
    )
    tags: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary dimension key-value pairs, e.g. {'region': 'EU', 'channel': 'web'}"
    )

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("Metric name cannot be empty")
        return cleaned


class MetricBatchCreate(BaseModel):
    """Payload for batch metric ingestion (up to 5,000 metrics)."""
    metrics: List[MetricCreate] = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Array of metric objects (1 to 5,000 items)"
    )


class MetricResponse(BaseModel):
    """Response representation of an ingested metric."""
    id: int
    name: str
    value: float
    unit: Optional[str]
    timestamp: datetime
    tags: Dict[str, Any]

    model_config = {"from_attributes": True}


class MetricBatchResponse(BaseModel):
    """Response for batch ingestion."""
    inserted: int
    status: str = "success"
    message: str


class MetricMetaResponse(BaseModel):
    """Metadata response for all metric names and tag keys discovered in DB."""
    metric_names: List[str]
    tag_keys: List[str]
    total_records: int
