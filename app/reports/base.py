"""Base class for all OmniMetrics report plugins."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession


class BaseReport(ABC):
    """Abstract Base Class defining the pluggable report strategy contract."""

    report_id: str
    display_name: str
    description: str

    @abstractmethod
    async def fetch_data(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Query, aggregate, and calculate metrics from database for the given period."""
        pass

    @abstractmethod
    async def render_charts(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        """Generate static chart images returned as a dict mapping chart_key -> PNG bytes."""
        pass

    @abstractmethod
    async def generate_pdf(
        self,
        data: Dict[str, Any],
        charts: Dict[str, bytes],
        ai_summary: Optional[str] = None,
    ) -> bytes:
        """Render Jinja2 HTML -> styled PDF bytes via WeasyPrint or Playwright."""
        pass

    @abstractmethod
    async def generate_excel(self, data: Dict[str, Any]) -> bytes:
        """Generate professional multi-tab .xlsx bytes with openpyxl."""
        pass

    async def sync_gsheets(self, data: Dict[str, Any], spreadsheet_id: str) -> bool:
        """Optional: Push data to Google Sheets."""
        return False

    @abstractmethod
    def format_telegram_caption(
        self,
        data: Dict[str, Any],
        ai_summary: Optional[str] = None,
    ) -> str:
        """Format a rich HTML/Markdown caption with key KPIs for the Telegram chat."""
        pass

    def to_info_dict(self) -> Dict[str, str]:
        """Metadata representation for API and Bot keyboards."""
        return {
            "report_id": self.report_id,
            "display_name": self.display_name,
            "description": self.description,
        }
