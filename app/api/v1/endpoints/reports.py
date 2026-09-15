"""Report execution, metadata and download endpoints."""
from datetime import datetime
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_api_key
from app.core.date_utils import parse_date_range
from app.reports.engine import report_engine
from app.reports.registry import report_registry
from app.schemas.report import ReportGenerateRequest, ReportInfoResponse

router = APIRouter()


@router.get(
    "",
    response_model=List[ReportInfoResponse],
    summary="List registered reports",
    dependencies=[Depends(verify_api_key)],
)
async def list_reports():
    """Return all available report plugins discovered in the system."""
    reports = report_registry.list_reports()
    return [r.to_info_dict() for r in reports]


@router.post(
    "/{report_id}/generate",
    summary="Generate report artifacts",
    dependencies=[Depends(verify_api_key)],
)
async def generate_report(
    report_id: str,
    payload: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a report across requested formats."""
    report = report_registry.get(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found.",
        )

    start_date, end_date = parse_date_range(
        payload.date_range, payload.start_date, payload.end_date
    )

    generated = await report_engine.generate_report(
        report_id=report_id,
        start_date=start_date,
        end_date=end_date,
        date_range_label=payload.date_range or "Custom",
        formats=payload.formats,
        spreadsheet_id=payload.spreadsheet_id,
        with_ai_summary=payload.with_ai_summary,
        session=db,
    )

    return {
        "status": "success",
        "report_id": generated.report_id,
        "display_name": generated.display_name,
        "start_date": generated.start_date.isoformat(),
        "end_date": generated.end_date.isoformat(),
        "ai_summary": generated.ai_summary,
        "caption": generated.telegram_caption,
        "has_pdf": generated.pdf_bytes is not None,
        "has_excel": generated.excel_bytes is not None,
        "has_png": generated.primary_card_png is not None,
        "gsheets_synced": generated.gsheets_synced,
    }


@router.get(
    "/{report_id}/download",
    summary="Direct download report file (PDF, Excel, or PNG)",
    dependencies=[Depends(verify_api_key)],
)
async def download_report_file(
    report_id: str,
    format: str = Query("pdf", description="Format to download: pdf, excel, or png"),
    date_range: str = Query("last_7_days", description="Named date range"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    """Generate and stream a single file artifact directly."""
    report = report_registry.get(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found.",
        )

    s_date, e_date = parse_date_range(date_range, start_date, end_date)

    generated = await report_engine.generate_report(
        report_id=report_id,
        start_date=s_date,
        end_date=e_date,
        date_range_label=date_range,
        formats=[format],
        session=db,
    )

    clean_fmt = format.lower().strip()
    filename_base = f"{report_id}_{s_date.strftime('%Y%m%d')}_{e_date.strftime('%Y%m%d')}"

    if clean_fmt == "pdf":
        if not generated.pdf_bytes:
            raise HTTPException(status_code=500, detail="PDF generation failed.")
        return Response(
            content=generated.pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.pdf"},
        )
    elif clean_fmt in ("excel", "xlsx"):
        if not generated.excel_bytes:
            raise HTTPException(status_code=500, detail="Excel generation failed.")
        return Response(
            content=generated.excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"},
        )
    elif clean_fmt == "png":
        if not generated.primary_card_png:
            raise HTTPException(status_code=500, detail="PNG preview generation failed.")
        return Response(
            content=generated.primary_card_png,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={filename_base}.png"},
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported download format '{format}'.")
