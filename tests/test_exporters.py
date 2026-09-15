"""Tests for ChartBuilder, ExcelExporter, PDFRenderer, and AIAnalyst services."""
from datetime import datetime
import io
import pytest

from app.services.ai_analyst import ai_analyst
from app.services.chart_builder import chart_builder
from app.services.excel_exporter import excel_exporter
from app.services.pdf_renderer import pdf_renderer


def test_chart_builder_line_chart():
    """Test generating a line chart and exporting to PNG bytes."""
    x = ["2026-09-01", "2026-09-02", "2026-09-03"]
    series = {"Revenue": [100.0, 150.0, 180.0]}
    fig = chart_builder.build_line_chart(x, series, title="Test Line Chart", fill_area=True)
    png_bytes = chart_builder.fig_to_png(fig)

    assert len(png_bytes) > 500
    assert png_bytes.startswith(b"\x89PNG")


def test_chart_builder_donut_chart():
    """Test generating a donut chart."""
    labels = ["Google Ads", "Organic", "Direct"]
    values = [500.0, 300.0, 200.0]
    fig = chart_builder.build_donut_chart(labels, values, title="Channel Share")
    png_bytes = chart_builder.fig_to_png(fig)

    assert len(png_bytes) > 500
    assert png_bytes.startswith(b"\x89PNG")


def test_chart_builder_kpi_card_badge():
    """Test rendering a standalone KPI card image."""
    card_bytes = chart_builder.build_kpi_card_image(
        title="Active Users",
        value_str="14,250",
        delta_str="12.5%",
        is_positive=True,
        subtitle="vs prior week",
    )
    assert len(card_bytes) > 500
    assert card_bytes.startswith(b"\x89PNG")


def test_excel_exporter_workbook():
    """Test building a multi-tab workbook with openpyxl."""
    wb = excel_exporter.create_workbook()
    ws = wb.active
    ws.title = "Summary"

    # Title
    excel_exporter.add_title_block(ws, "Test Executive Report", "Subtitle line")

    # KPI cards
    kpis = [
        {"title": "Revenue", "value": "$50,000", "delta": "14.2%", "is_positive": True},
        {"title": "Orders", "value": "520", "delta": "3.1%", "is_positive": False},
    ]
    excel_exporter.add_kpi_cards(ws, kpis, start_row=4)

    # Table
    headers = ["Item", "Count", "Amount"]
    rows = [["Alpha", 10, 100.50], ["Beta", 20, 200.75]]
    excel_exporter.add_table(ws, headers, rows, start_row=8)

    buf = excel_exporter.to_bytes(wb)
    assert len(buf) > 1000
    assert buf.startswith(b"PK")


@pytest.mark.asyncio
async def test_pdf_renderer_html_and_pdf():
    """Test HTML rendering and compiling to PDF."""
    context = {
        "report_title": "Test Report",
        "date_range_label": "Last 7 Days",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "ai_summary": "• 🚀 Key Gain: Growth detected\n• 🎯 Action: Scale channels",
        "kpis": [{"title": "Revenue", "value": "$10,000", "delta": "5%", "is_positive": True}],
        "charts": [],
        "tables": [{
            "title": "Data",
            "headers": ["Col 1", "Col 2"],
            "rows": [["Val A", "Val B"]],
        }],
    }

    html = pdf_renderer.render_html("base_report.html", context)
    assert "Test Report" in html
    assert "Executive Intelligence Briefing" in html

    pdf_bytes = await pdf_renderer.render_pdf(html)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_ai_analyst_heuristic_summary():
    """Test heuristic executive briefing generation."""
    metrics_summary = {
        "kpis": {"revenue": "$15,000", "orders": "120"},
        "deltas": {"revenue": 18.5, "refunds": -4.2},
    }
    summary = await ai_analyst.generate_summary("E-Commerce Test", metrics_summary)
    assert "Key Gain" in summary
    assert "Drop / Friction Point" in summary
    assert "Anomaly / Pattern" in summary
    assert "Recommended Action" in summary
    assert "•" in summary
