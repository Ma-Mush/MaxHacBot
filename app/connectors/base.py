"""Base connector interface for external data sources and marketplace integrations."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import MetricRecord


class BaseConnector(ABC):
    """Abstract Base Class for external data connectors (Wildberries, Ozon, 1C, etc.)."""

    name: str = "base"
    display_name: str = "Base Connector"
    description: str = "Abstract external integration connector"

    @abstractmethod
    async def fetch_and_ingest(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        session: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fetch remote metrics/sales and ingest them into database."""
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Verify API credentials and connectivity."""
        pass
