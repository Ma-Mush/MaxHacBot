"""OmniMetrics CLI: Tooling for seeding demo data, testing reports, scaffolding plugins, and running services."""
import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Optional
import click

# Ensure current directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.config import settings
from app.core.database import async_session_maker, close_db, init_db
from app.core.date_utils import parse_date_range
from app.models.metric import MetricRecord
from app.reports.engine import report_engine
from app.reports.registry import report_registry


def run_async(coro):
    """Helper to run async coroutines in synchronous click commands."""
    return asyncio.run(coro)


@click.group()
def cli():
    """OmniMetrics Hub CLI: Manage metrics, report plugins, and testing."""
    pass


@cli.command("seed-demo")
@click.option("--days", default=60, help="Number of historical days to seed (default: 60).")
@click.option("--clear", is_flag=True, default=False, help="Clear existing records before seeding.")
def seed_demo(days: int, clear: bool):
    """Seed the database with realistic e-commerce and server telemetry metrics."""
    async def _seed():
        await init_db()
        async with async_session_maker() as session:
            if clear:
                click.secho("Clearing existing metrics records...", fg="yellow")
                from sqlalchemy import delete
                await session.execute(delete(MetricRecord))
                await session.commit()

            click.secho(f"🌱 Generating {days} days of realistic telemetry data...", fg="cyan")
            now = datetime.now(timezone.utc)
            records = []

            channels = ["google_ads", "meta_ads", "organic_search", "email_marketing", "direct"]
            regions = ["US", "EU", "APAC", "LATAM"]
            hosts = ["api-prod-01", "api-prod-02", "worker-prod-01"]

            for day_offset in range(days, -1, -1):
                day_base = now - timedelta(days=day_offset)
                day_of_week = day_base.weekday()
                # Weekend boost or dip
                weekend_mult = 1.3 if day_of_week in (4, 5, 6) else 1.0

                # 1. E-Commerce Metrics per day
                daily_visitors = int(random.randint(1200, 3500) * weekend_mult)
                daily_orders = int(daily_visitors * random.uniform(0.022, 0.045))
                avg_order_value = random.uniform(55.0, 115.0)
                daily_revenue = round(daily_orders * avg_order_value, 2)
                daily_refunds = round(daily_revenue * random.uniform(0.015, 0.045), 2)

                # Split revenue across multiple transactions throughout the day
                num_chunks = random.randint(3, 6)
                for _ in range(num_chunks):
                    chunk_rev = round(daily_revenue / num_chunks * random.uniform(0.8, 1.2), 2)
                    chunk_orders = max(1, int(daily_orders / num_chunks))
                    event_time = day_base.replace(
                        hour=random.randint(0, 23),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59),
                    )
                    ch = random.choice(channels)
                    rg = random.choice(regions)

                    records.append(
                        MetricRecord(
                            name="revenue",
                            value=chunk_rev,
                            unit="USD",
                            timestamp=event_time,
                            tags={"channel": ch, "region": rg},
                        )
                    )
                    records.append(
                        MetricRecord(
                            name="orders_count",
                            value=float(chunk_orders),
                            unit="pcs",
                            timestamp=event_time,
                            tags={"channel": ch, "region": rg},
                        )
                    )

                # Daily aggregated aggregates
                records.append(
                    MetricRecord(
                        name="refunds",
                        value=daily_refunds,
                        unit="USD",
                        timestamp=day_base.replace(hour=23, minute=50),
                        tags={"source": "stripe"},
                    )
                )
                records.append(
                    MetricRecord(
                        name="visitors",
                        value=float(daily_visitors),
                        unit="users",
                        timestamp=day_base.replace(hour=23, minute=55),
                        tags={"source": "google_analytics"},
                    )
                )

                # 2. Server Telemetry Metrics
                for host in hosts:
                    cpu_val = round(random.uniform(25.0, 68.0) * (1.2 if day_of_week < 5 else 0.85), 1)
                    mem_val = round(random.uniform(2800.0, 5200.0), 1)
                    req_val = round(random.uniform(20000.0, 85000.0))
                    err_val = round(random.uniform(2.0, 35.0))
                    lat_val = round(random.uniform(45.0, 115.0), 1)

                    sample_time = day_base.replace(hour=14, minute=random.randint(0, 59))
                    records.append(MetricRecord(name="cpu_utilization", value=cpu_val, unit="%", timestamp=sample_time, tags={"host": host}))
                    records.append(MetricRecord(name="memory_usage_mb", value=mem_val, unit="MB", timestamp=sample_time, tags={"host": host}))
                    records.append(MetricRecord(name="http_requests_total", value=req_val, unit="reqs", timestamp=sample_time, tags={"host": host}))
                    records.append(MetricRecord(name="http_5xx_errors", value=err_val, unit="errs", timestamp=sample_time, tags={"host": host}))
                    records.append(MetricRecord(name="api_latency_ms", value=lat_val, unit="ms", timestamp=sample_time, tags={"host": host}))

            # Batch insert in chunks of 500
            chunk_size = 500
            for i in range(0, len(records), chunk_size):
                session.add_all(records[i : i + chunk_size])
                await session.commit()

            click.secho(f"✅ Successfully seeded {len(records):,} realistic metric records across {days} days!", fg="green", bold=True)

        await close_db()

    run_async(_seed())


@cli.command("sync-wb")
@click.option("--days", default=14, help="Number of past days of sales to sync (default: 14).")
@click.option("--mock", is_flag=True, default=False, help="Force simulated sandbox data for demo.")
@click.option("--api-key", default=None, help="Wildberries Statistics API Key.")
def sync_wb_cmd(days: int, mock: bool, api_key: Optional[str]):
    """Synchronize sales and returns directly from Wildberries Statistics API."""
    async def _sync():
        await init_db()
        from app.connectors.wildberries import WildberriesConnector
        connector = WildberriesConnector(api_key=api_key)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        click.secho(f"\n🛒 Connecting to Wildberries ({'Sandbox/Demo' if (mock or not connector.is_configured()) else 'Live API'})...", fg="cyan", bold=True)
        res = await connector.fetch_and_ingest(start_date=start_date, end_date=end_date, force_mock=mock)
        if not res.get("success"):
            click.secho(f"❌ Synchronization failed: {res.get('message')}", fg="red")
            return

        click.secho(f"✅ Successfully synchronized {res['sales_count']} Wildberries transactions ({res['metrics_created']} metric records)!", fg="green", bold=True)
        click.echo(f"   📅 Time Window:     {res['date_from']} -> {res['date_to']}")
        click.echo(f"   💰 Total Revenue:    {res['total_revenue']:,.2f} RUB")
        click.echo(f"   📦 Orders Count:     {res['total_orders']}")
        click.echo(f"   🔄 Returns/Cancels:  {res['total_refunds']:,.2f} RUB")
        if res.get("top_regions"):
            click.echo(f"   📍 Top Regions:      {', '.join(f'{k} ({v})' for k, v in list(res['top_regions'].items())[:3])}")
        if res.get("top_warehouses"):
            click.echo(f"   🏭 Top Warehouses:    {', '.join(f'{k} ({v})' for k, v in list(res['top_warehouses'].items())[:3])}")
        click.secho("\n✨ Telemetry updated! Generate executive briefing with 'python cli.py test-report ecommerce_summary'.\n", fg="cyan")
        await close_db()

    run_async(_sync())


@cli.command("sync-ozon")
@click.option("--days", default=14, help="Number of past days of postings to sync (default: 14).")
@click.option("--mock", is_flag=True, default=False, help="Force simulated sandbox data for demo.")
@click.option("--client-id", default=None, help="Ozon Seller Client ID.")
@click.option("--api-key", default=None, help="Ozon Seller API Key.")
def sync_ozon_cmd(days: int, mock: bool, client_id: Optional[str], api_key: Optional[str]):
    """Synchronize postings and financial metrics directly from Ozon Seller API."""
    async def _sync():
        await init_db()
        from app.connectors.ozon import OzonConnector
        connector = OzonConnector(client_id=client_id, api_key=api_key)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        click.secho(f"\n🛒 Connecting to Ozon ({'Sandbox/Demo' if (mock or not connector.is_configured()) else 'Live API'})...", fg="blue", bold=True)
        res = await connector.fetch_and_ingest(start_date=start_date, end_date=end_date, force_mock=mock)
        if not res.get("success"):
            click.secho(f"❌ Synchronization failed: {res.get('message')}", fg="red")
            return

        click.secho(f"✅ Successfully synchronized {res['postings_count']} Ozon postings ({res['metrics_created']} metric records)!", fg="green", bold=True)
        click.echo(f"   📅 Time Window:     {res['date_from']} -> {res['date_to']}")
        click.echo(f"   💰 Total Revenue:    {res['total_revenue']:,.2f} RUB")
        click.echo(f"   📦 Orders Count:     {res['total_orders']}")
        click.echo(f"   🔄 Returns/Cancels:  {res['total_refunds']:,.2f} RUB")
        if res.get("top_clusters"):
            click.echo(f"   📍 Top Clusters:     {', '.join(f'{k} ({v})' for k, v in list(res['top_clusters'].items())[:3])}")
        if res.get("top_warehouses"):
            click.echo(f"   🏭 Top Warehouses:    {', '.join(f'{k} ({v})' for k, v in list(res['top_warehouses'].items())[:3])}")
        click.secho("\n✨ Telemetry updated! Generate executive briefing with 'python cli.py test-report ecommerce_summary'.\n", fg="cyan")
        await close_db()

    run_async(_sync())


@cli.command("sync-yandex")
@click.option("--days", default=14, help="Number of past days of orders to sync (default: 14).")
@click.option("--mock", is_flag=True, default=False, help="Force simulated sandbox data for demo.")
@click.option("--campaign-id", default=None, help="Yandex Market Campaign ID.")
@click.option("--api-key", default=None, help="Yandex Market Partner API Key.")
def sync_yandex_cmd(days: int, mock: bool, campaign_id: Optional[str], api_key: Optional[str]):
    """Synchronize orders and sales telemetry directly from Yandex Market Partner API."""
    async def _sync():
        await init_db()
        from app.connectors.yandex_market import YandexMarketConnector
        connector = YandexMarketConnector(campaign_id=campaign_id, api_key=api_key)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        click.secho(f"\n🛒 Connecting to Yandex Market ({'Sandbox/Demo' if (mock or not connector.is_configured()) else 'Live API'})...", fg="yellow", bold=True)
        res = await connector.fetch_and_ingest(start_date=start_date, end_date=end_date, force_mock=mock)
        if not res.get("success"):
            click.secho(f"❌ Synchronization failed: {res.get('message')}", fg="red")
            return

        click.secho(f"✅ Successfully synchronized {res['orders_count']} Yandex Market orders ({res['metrics_created']} metric records)!", fg="green", bold=True)
        click.echo(f"   📅 Time Window:     {res['date_from']} -> {res['date_to']}")
        click.echo(f"   💰 Total Revenue:    {res['total_revenue']:,.2f} RUB")
        click.echo(f"   📦 Orders Count:     {res['total_orders']}")
        click.echo(f"   🔄 Returns/Cancels:  {res['total_refunds']:,.2f} RUB")
        if res.get("top_regions"):
            click.echo(f"   📍 Top Regions:      {', '.join(f'{k} ({v})' for k, v in list(res['top_regions'].items())[:3])}")
        if res.get("top_warehouses"):
            click.echo(f"   🏭 Top Warehouses:    {', '.join(f'{k} ({v})' for k, v in list(res['top_warehouses'].items())[:3])}")
        click.secho("\n✨ Telemetry updated! Generate executive briefing with 'python cli.py test-report ecommerce_summary'.\n", fg="cyan")
        await close_db()

    run_async(_sync())


@cli.command("sync-sbermarket")
@click.option("--days", default=14, help="Number of past days of orders to sync (default: 14).")
@click.option("--mock", is_flag=True, default=False, help="Force simulated sandbox data for demo.")
@click.option("--api-token", default=None, help="SberMarket / Kuper API Token.")
@click.option("--merchant-id", default=None, help="SberMarket / Kuper Merchant ID.")
def sync_sbermarket_cmd(days: int, mock: bool, api_token: Optional[str], merchant_id: Optional[str]):
    """Synchronize orders and retail GMV directly from SberMarket / Kuper Merchant API."""
    async def _sync():
        await init_db()
        from app.connectors.sbermarket import SberMarketConnector
        connector = SberMarketConnector(api_token=api_token, merchant_id=merchant_id)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        click.secho(f"\n🛒 Connecting to SberMarket/Купер ({'Sandbox/Demo' if (mock or not connector.is_configured()) else 'Live API'})...", fg="green", bold=True)
        res = await connector.fetch_and_ingest(start_date=start_date, end_date=end_date, force_mock=mock)
        if not res.get("success"):
            click.secho(f"❌ Synchronization failed: {res.get('message')}", fg="red")
            return

        click.secho(f"✅ Successfully synchronized {res['orders_count']} SberMarket/Купер orders ({res['metrics_created']} metric records)!", fg="green", bold=True)
        click.echo(f"   📅 Time Window:     {res['date_from']} -> {res['date_to']}")
        click.echo(f"   💰 Total Revenue:    {res['total_revenue']:,.2f} RUB")
        click.echo(f"   📦 Orders Count:     {res['total_orders']}")
        click.echo(f"   🔄 Returns/Cancels:  {res['total_refunds']:,.2f} RUB")
        if res.get("top_cities"):
            click.echo(f"   📍 Top Cities:       {', '.join(f'{k} ({v})' for k, v in list(res['top_cities'].items())[:3])}")
        if res.get("top_stores"):
            click.echo(f"   🏬 Top Stores:       {', '.join(f'{k} ({v})' for k, v in list(res['top_stores'].items())[:3])}")
        click.secho("\n✨ Telemetry updated! Generate executive briefing with 'python cli.py test-report ecommerce_summary'.\n", fg="cyan")
        await close_db()

    run_async(_sync())





@cli.command("list-reports")
def list_reports():
    """List all registered report plugins and their metadata."""
    report_registry.discover()
    reports = report_registry.list_reports()

    click.secho("\n📋 Registered OmniMetrics Report Plugins:\n", fg="cyan", bold=True)
    if not reports:
        click.secho("No report plugins found. Add reports in app/custom_reports/", fg="yellow")
        return

    for idx, r in enumerate(reports, start=1):
        click.secho(f"{idx}. {r.display_name} [{r.report_id}]", fg="green", bold=True)
        click.echo(f"   Description: {r.description}")
        click.echo(f"   Module:      {r.__class__.__module__}.{r.__class__.__name__}\n")


@cli.command("test-report")
@click.argument("report_id")
@click.option("--days", default=7, help="Number of past days for report window (default: 7).")
@click.option("--output-dir", default="./output", help="Directory to save generated artifacts.")
def test_report(report_id: str, days: int, output_dir: str):
    """Generate all report formats locally to ./output/ for instant verification."""
    async def _test():
        await init_db()
        report_registry.discover()

        report = report_registry.get(report_id)
        if not report:
            click.secho(f"❌ Error: Report '{report_id}' not found.", fg="red", err=True)
            click.echo("Available reports: " + ", ".join(r.report_id for r in report_registry.list_reports()))
            sys.exit(1)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)
        end_date = now

        click.secho(f"\n🚀 Testing report '{report_id}' over last {days} days...", fg="cyan", bold=True)

        async with async_session_maker() as session:
            generated = await report_engine.generate_report(
                report_id=report_id,
                start_date=start_date,
                end_date=end_date,
                date_range_label=f"Last {days} Days",
                formats=["all"],
                session=session,
            )

        click.secho("\n--- TELEGRAM CAPTION PREVIEW ---", fg="magenta")
        click.echo(generated.telegram_caption)
        click.secho("--------------------------------\n", fg="magenta")

        # Save Preview PNG
        if generated.primary_card_png:
            card_file = out_path / f"{report_id}_preview.png"
            card_file.write_bytes(generated.primary_card_png)
            click.secho(f"🖼️ Saved preview card: {card_file.resolve()}", fg="green")

        # Save all rendered charts
        for chart_name, chart_bytes in generated.charts.items():
            c_file = out_path / f"{report_id}_chart_{chart_name}.png"
            c_file.write_bytes(chart_bytes)
            click.secho(f"📈 Saved chart: {c_file.resolve()}", fg="green")

        # Save PDF
        if generated.pdf_bytes:
            pdf_file = out_path / f"{report_id}_report.pdf"
            pdf_file.write_bytes(generated.pdf_bytes)
            click.secho(f"📄 Saved PDF report:  {pdf_file.resolve()}", fg="green", bold=True)
        else:
            click.secho("⚠️ PDF report generation skipped or engine unavailable.", fg="yellow")

        # Save Excel
        if generated.excel_bytes:
            excel_file = out_path / f"{report_id}_data.xlsx"
            excel_file.write_bytes(generated.excel_bytes)
            click.secho(f"📊 Saved Excel sheet: {excel_file.resolve()}", fg="green", bold=True)

        # Save Caption text
        caption_file = out_path / f"{report_id}_caption.txt"
        caption_file.write_text(generated.telegram_caption, encoding="utf-8")

        click.secho(f"\n✨ Test completed! All artifacts generated in '{output_dir}'.\n", fg="cyan", bold=True)
        await close_db()

    run_async(_test())


@cli.command("create-plugin")
@click.argument("name")
def create_plugin(name: str):
    """Scaffold a new custom report plugin in app/custom_reports/."""
    clean_name = name.lower().strip().replace("-", "_")
    if not clean_name.endswith("_report"):
        filename = f"{clean_name}_report.py"
        report_id = clean_name
    else:
        filename = f"{clean_name}.py"
        report_id = clean_name.replace("_report", "")

    class_name = "".join(word.capitalize() for word in report_id.split("_")) + "Report"

    target_path = Path(__file__).resolve().parent / "app" / "custom_reports" / filename
    if target_path.exists():
        click.secho(f"❌ Plugin file already exists at: {target_path}", fg="red")
        return

    template = f'''"""Custom Report Plugin: {class_name}."""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import MetricRecord
from app.reports.base import BaseReport
from app.services.chart_builder import chart_builder
from app.services.excel_exporter import excel_exporter
from app.services.pdf_renderer import pdf_renderer


class {class_name}(BaseReport):
    report_id = "{report_id}"
    display_name = "📊 {class_name.replace('Report', '')} Overview"
    description = "Custom analytics report plugin for {report_id}"

    async def fetch_data(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Query and aggregate your metrics."""
        query = (
            select(MetricRecord.name, func.sum(MetricRecord.value).label("total"))
            .where(MetricRecord.timestamp >= start_date)
            .where(MetricRecord.timestamp <= end_date)
            .group_by(MetricRecord.name)
        )
        res = await session.execute(query)
        data = {{row.name: float(row.total) for row in res.all()}}
        
        return {{
            "metrics": data,
            "kpis": {{"Total Metrics Tracked": len(data)}},
            "deltas": {{}},
        }}

    async def render_charts(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        charts: Dict[str, bytes] = {{}}
        metrics = data.get("metrics", {{}})
        if metrics:
            fig = chart_builder.build_bar_chart(
                categories=list(metrics.keys()),
                series={{"Sum": list(metrics.values())}},
                title="{class_name} Ingestion Totals",
            )
            charts["main_bar"] = chart_builder.fig_to_png(fig)
            charts["preview_card"] = chart_builder.build_kpi_card_image(
                title="Metrics Tracked",
                value_str=str(len(metrics)),
                subtitle="{report_id}",
            )
        return charts

    async def generate_pdf(
        self,
        data: Dict[str, Any],
        charts: Dict[str, bytes],
        ai_summary: Optional[str] = None,
    ) -> bytes:
        kpis = [{{"title": "Metrics Count", "value": str(len(data.get("metrics", {{}})))}}]
        chart_containers = []
        if "main_bar" in charts:
            chart_containers.append({{
                "title": "Aggregated Totals",
                "image_base64": pdf_renderer.chart_bytes_to_base64(charts["main_bar"]),
            }})
        tables = [{{
            "title": "Metrics Breakdown",
            "headers": ["Metric", "Aggregated Sum"],
            "rows": [[k, f"{{v:,.2f}}"] for k, v in data.get("metrics", {{}}).items()],
        }}]
        context = {{
            "report_title": self.display_name,
            "date_range_label": data.get("date_range_label", "Selected Period"),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "ai_summary": ai_summary,
            "kpis": kpis,
            "charts": chart_containers,
            "tables": tables,
        }}
        html = pdf_renderer.render_html("base_report.html", context)
        return await pdf_renderer.render_pdf(html)

    async def generate_excel(self, data: Dict[str, Any]) -> bytes:
        wb = excel_exporter.create_workbook()
        ws = wb.active
        ws.title = "Data"
        headers = ["Metric Name", "Value"]
        rows = [[k, v] for k, v in data.get("metrics", {{}}).items()]
        excel_exporter.add_table(ws, headers, rows, start_row=1)
        return excel_exporter.to_bytes(wb)

    def format_telegram_caption(
        self,
        data: Dict[str, Any],
        ai_summary: Optional[str] = None,
    ) -> str:
        lines = [
            f"📊 <b>{{self.display_name}}</b>",
            f"🗓 <i>Window: {{data.get('date_range_label', 'Selected Window')}}</i>",
            "",
        ]
        for k, v in list(data.get("metrics", {{}}).items())[:5]:
            lines.append(f"• <b>{{k}}</b>: <code>{{v:,.2f}}</code>")
        if ai_summary:
            lines.append(f"\n🧠 <b>AI Briefing:</b>\n{{ai_summary}}")
        return "\\n".join(lines)
'''
    target_path.write_text(template, encoding="utf-8")
    click.secho(f"🎉 Created report plugin scaffold: {target_path}", fg="green", bold=True)
    click.echo(f"Report ID: {report_id}")
    click.echo("This report will be auto-discovered by OmniMetrics Hub!")


@cli.command("run-api")
@click.option("--host", default="0.0.0.0", help="Host address to bind to.")
@click.option("--port", default=8000, help="Port to listen on.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload for development.")
def run_api(host: str, port: int, reload: bool):
    """Run the FastAPI REST ingestion and reporting service."""
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


@cli.command("run-bot")
def run_bot():
    """Run the Aiogram Telegram bot and background report scheduler."""
    from app.bot.bot import run_bot as start_bot
    asyncio.run(start_bot())


@cli.command("run-max-bot")
def run_max_bot_cmd():
    """Run the MAX Messenger Bot with polling loop."""
    from app.max_bot.runner import run_max_bot as start_max_bot
    asyncio.run(start_max_bot())


@cli.command("run-all")
@click.option("--port", default=8000, help="API port.")
def run_all(port: int):
    """Run FastAPI, MAX Bot, and Telegram Bot concurrently in a unified event loop."""
    import uvicorn
    from app.bot.bot import run_bot as start_bot
    from app.max_bot.runner import run_max_bot as start_max_bot

    async def _run_both():
        config = uvicorn.Config("app.main:app", host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        tasks = [server.serve()]

        # Launch MAX Messenger Bot
        if settings.MAX_BOT_TOKEN and settings.MAX_BOT_TOKEN != "your_max_bot_token_here":
            click.secho("🚀 Starting MAX Messenger Bot runner...", fg="green")
            tasks.append(start_max_bot())
        else:
            click.secho("ℹ️ MAX_BOT_TOKEN not set; MAX Bot runner in standby.", fg="blue")

        # Launch Telegram Bot if configured
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_TOKEN != "your_telegram_bot_token_here":
            click.secho("🚀 Starting Telegram Bot runner...", fg="green")
            tasks.append(start_bot())
        else:
            click.secho("ℹ️ TELEGRAM_BOT_TOKEN not set.", fg="yellow")

        await asyncio.gather(*tasks)

    asyncio.run(_run_both())


if __name__ == "__main__":
    cli()

