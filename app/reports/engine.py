"""Execution engine for orchestrating report generation, AI analysis, and multi-format exports."""
from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.base import BaseReport
from app.reports.registry import report_registry
from app.services.ai_analyst import ai_analyst

logger = logging.getLogger(__name__)


@dataclass
class GeneratedReport:
    """Container holding all generated artifacts for a report execution."""
    report_id: str
    display_name: str
    start_date: datetime
    end_date: datetime
    date_range_label: str
    data: Dict[str, Any]
    ai_summary: Optional[str] = None
    telegram_caption: str = ""
    charts: Dict[str, bytes] = field(default_factory=dict)
    primary_card_png: Optional[bytes] = None
    pdf_bytes: Optional[bytes] = None
    excel_bytes: Optional[bytes] = None
    gsheets_synced: bool = False


class ReportEngine:
    """Engine executing report plugins and assembling output formats."""

    async def generate_report(
        self,
        report_id: str,
        start_date: datetime,
        end_date: datetime,
        date_range_label: str = "Selected Period",
        formats: Optional[Sequence[str]] = None,
        spreadsheet_id: Optional[str] = None,
        with_ai_summary: bool = True,
        session: Optional[AsyncSession] = None,
    ) -> GeneratedReport:
        """Run the full report generation pipeline."""
        report = report_registry.get(report_id)
        if not report:
            raise ValueError(f"Report '{report_id}' not found in registry.")

        if formats is None:
            formats = ["pdf", "excel", "png", "summary"]

        formats_set = set(f.lower().strip() for f in formats)

        # 1. Fetch raw and aggregated data
        logger.info(f"Fetching data for report '{report_id}' ({start_date.isoformat()} to {end_date.isoformat()})...")
        data = await report.fetch_data(session, start_date=start_date, end_date=end_date)
        data["date_range_label"] = date_range_label
        data["start_date"] = start_date
        data["end_date"] = end_date

        # 2. Render charts
        logger.info(f"Rendering charts for report '{report_id}'...")
        charts = await report.render_charts(data)

        # 3. AI Summary
        ai_summary_text: Optional[str] = None
        if with_ai_summary:
            logger.info(f"Generating AI executive briefing for '{report_id}'...")
            ai_summary_text = await ai_analyst.generate_summary(
                report_title=report.display_name,
                metrics_summary=data,
            )

        # 4. Telegram Caption
        telegram_caption = report.format_telegram_caption(data, ai_summary=ai_summary_text)

        # 5. Primary PNG Preview Card
        primary_card_png = None
        if "preview_card" in charts:
            primary_card_png = charts["preview_card"]
        elif charts:
            primary_card_png = next(iter(charts.values()))

        # 6. PDF Generation
        pdf_bytes = None
        if "pdf" in formats_set or "all" in formats_set:
            logger.info(f"Generating PDF for report '{report_id}'...")
            try:
                pdf_bytes = await report.generate_pdf(data, charts, ai_summary=ai_summary_text)
            except Exception as exc:
                logger.error(f"Failed to generate PDF for '{report_id}': {exc}", exc_info=True)

        # 7. Excel Generation
        excel_bytes = None
        if "excel" in formats_set or "all" in formats_set:
            logger.info(f"Generating Excel for report '{report_id}'...")
            try:
                excel_bytes = await report.generate_excel(data)
            except Exception as exc:
                logger.error(f"Failed to generate Excel for '{report_id}': {exc}", exc_info=True)

        # 8. Google Sheets Sync
        gsheets_synced = False
        if ("gsheets" in formats_set or "all" in formats_set) and spreadsheet_id:
            logger.info(f"Syncing report '{report_id}' to Google Sheets ({spreadsheet_id})...")
            try:
                gsheets_synced = await report.sync_gsheets(data, spreadsheet_id=spreadsheet_id)
            except Exception as exc:
                logger.error(f"Failed to sync Google Sheets for '{report_id}': {exc}", exc_info=True)

        return GeneratedReport(
            report_id=report_id,
            display_name=report.display_name,
            start_date=start_date,
            end_date=end_date,
            date_range_label=date_range_label,
            data=data,
            ai_summary=ai_summary_text,
            telegram_caption=telegram_caption,
            charts=charts,
            primary_card_png=primary_card_png,
            pdf_bytes=pdf_bytes,
            excel_bytes=excel_bytes,
            gsheets_synced=gsheets_synced,
        )


report_engine = ReportEngine()
