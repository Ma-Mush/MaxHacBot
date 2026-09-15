"""Universal metric record database model."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    JSON,
)
from sqlalchemy.dialects import postgresql
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Use native JSONB on PostgreSQL and standard JSON on SQLite/others
JSONBType = JSON().with_variant(postgresql.JSONB(none_as_null=True), "postgresql")


class MetricRecord(Base):
    """Universal Metric Record storing arbitrary numerical metrics and dimensions."""
    __tablename__ = "metrics"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(64), nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )
    tags = Column(JSONBType, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_metrics_name_timestamp", "name", "timestamp"),
        Index(
            "ix_metrics_tags_gin",
            "tags",
            postgresql_using="gin",
        ),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to Python dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tags": self.tags or {},
        }

    def __repr__(self) -> str:
        return f"<MetricRecord id={self.id} name='{self.name}' value={self.value} {self.unit or ''} at {self.timestamp}>"
