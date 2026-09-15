"""Tests for Report Plugins and Report Engine execution."""
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import MetricRecord
from app.reports.engine import report_engine
from app.reports.registry import report_registry


@pytest.mark.asyncio
async def test_report_registry_discovery():
    """Verify built-in reports are properly discovered and loaded."""
    report_registry.discover()
    reports = report_registry.list_reports()
    ids = [r.report_id for r in reports]

    assert "default_metric_report" in ids
    assert "ecommerce_summary" in ids


@pytest.mark.asyncio
async def test_ecommerce_summary_execution(db_session: AsyncSession):
    """Test EcommerceSummaryReport end-to-end data fetching and generation."""
    now = datetime.now(timezone.utc)
    # Seed current period records
    db_session.add_all([
        MetricRecord(name="revenue", value=1500.0, unit="USD", timestamp=now - timedelta(days=1), tags={"channel": "google_ads", "region": "US"}),
        MetricRecord(name="revenue", value=2500.0, unit="USD", timestamp=now - timedelta(days=2), tags={"channel": "direct", "region": "EU"}),
        MetricRecord(name="orders_count", value=40.0, unit="pcs", timestamp=now - timedelta(days=1)),
        MetricRecord(name="refunds", value=80.0, unit="USD", timestamp=now - timedelta(days=1)),
        MetricRecord(name="visitors", value=1000.0, unit="users", timestamp=now - timedelta(days=1)),
    ])
    # Seed prior period records
    db_session.add_all([
        MetricRecord(name="revenue", value=3000.0, unit="USD", timestamp=now - timedelta(days=9)),
        MetricRecord(name="orders_count", value=30.0, unit="pcs", timestamp=now - timedelta(days=9)),
    ])
    await db_session.commit()

    report = report_registry.get("ecommerce_summary")
    assert report is not None

    start_date = now - timedelta(days=7)
    end_date = now

    data = await report.fetch_data(db_session, start_date=start_date, end_date=end_date)
    assert data["summary"]["revenue"] == 4000.0
    assert data["summary"]["orders"] == 40
    assert data["summary"]["aov"] == 100.0
    assert data["summary"]["refunds"] == 80.0
    assert data["summary"]["revenue_delta"] > 0

    # Test charts
    charts = await report.render_charts(data)
    assert "revenue_trend" in charts
    assert "channel_donut" in charts
    assert "preview_card" in charts
    assert len(charts["revenue_trend"]) > 0

    # Test Telegram caption
    caption = report.format_telegram_caption(data, ai_summary="• 🚀 Test summary")
    assert "Executive E-Commerce Briefing" in caption
    assert "$4,000.00" in caption
    assert "Test summary" in caption

    # Test Excel generation
    excel_bytes = await report.generate_excel(data)
    assert len(excel_bytes) > 1000
    assert excel_bytes.startswith(b"PK")  # ZIP header for xlsx

    # Test PDF generation
    pdf_bytes = await report.generate_pdf(data, charts, ai_summary="• 🚀 Test gain")
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_default_metric_report_execution(db_session: AsyncSession):
    """Test DefaultMetricReport with arbitrary metrics."""
    now = datetime.now(timezone.utc)
    db_session.add_all([
        MetricRecord(name="custom_kpi", value=100.0, timestamp=now - timedelta(days=1)),
        MetricRecord(name="custom_kpi", value=200.0, timestamp=now - timedelta(days=2)),
        MetricRecord(name="latency", value=45.0, timestamp=now - timedelta(days=1)),
    ])
    await db_session.commit()

    report = report_registry.get("default_metric_report")
    assert report is not None

    start_date = now - timedelta(days=7)
    end_date = now

    data = await report.fetch_data(db_session, start_date, end_date)
    assert "custom_kpi" in data["metrics"]
    assert data["metrics"]["custom_kpi"]["sum"] == 300.0

    charts = await report.render_charts(data)
    assert "preview_card" in charts

    # Excel
    excel_bytes = await report.generate_excel(data)
    assert excel_bytes.startswith(b"PK")

    # PDF
    pdf_bytes = await report.generate_pdf(data, charts, ai_summary="• Briefing")
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_report_engine_full_run(db_session: AsyncSession):
    """Test ReportEngine orchestrating complete generation workflow."""
    now = datetime.now(timezone.utc)
    db_session.add(MetricRecord(name="revenue", value=500.0, timestamp=now - timedelta(days=1)))
    await db_session.commit()

    generated = await report_engine.generate_report(
        report_id="ecommerce_summary",
        start_date=now - timedelta(days=7),
        end_date=now,
        date_range_label="Last 7 Days",
        formats=["all"],
        with_ai_summary=True,
        session=db_session,
    )

    assert generated.report_id == "ecommerce_summary"
    assert generated.pdf_bytes is not None
    assert generated.excel_bytes is not None
    assert generated.primary_card_png is not None
    assert len(generated.telegram_caption) > 20
    assert generated.ai_summary is not None
