"""Report request and response schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReportInfoResponse(BaseModel):
    """Metadata about a registered report plugin."""
    report_id: str
    display_name: str
    description: str


class ReportGenerateRequest(BaseModel):
    """Payload to trigger report generation via API."""
    date_range: Optional[str] = Field(
        "last_7_days",
        description="Named date range: today, yesterday, last_7_days, last_30_days, this_month, or custom"
    )
    start_date: Optional[datetime] = Field(None, description="Start date/time (UTC) if date_range='custom'")
    end_date: Optional[datetime] = Field(None, description="End date/time (UTC) if date_range='custom'")
    formats: List[str] = Field(
        default_factory=lambda: ["summary", "pdf", "excel", "png"],
        description="Formats to generate: summary, pdf, excel, png, gsheets"
    )
    spreadsheet_id: Optional[str] = Field(
        None,
        description="Optional Google Spreadsheet ID for gsheets export"
    )
    with_ai_summary: bool = Field(True, description="Whether to include AI executive briefing")
