"""Universal Builtin Report for arbitrary metrics in OmniMetrics Hub."""
from collections import defaultdict
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.date_utils import get_previous_period
from app.models.metric import MetricRecord
from app.reports.base import BaseReport
from app.services.chart_builder import chart_builder
from app.services.excel_exporter import excel_exporter
from app.services.gsheets_exporter import gsheets_exporter
from app.services.pdf_renderer import pdf_renderer

logger = logging.getLogger(__name__)


class DefaultMetricReport(BaseReport):
    """General-purpose report analyzing all metrics within the designated window."""

    report_id = "default_metric_report"
    display_name = "🌐 Universal Metrics Overview"
    description = "Holistic executive breakdown and trends for all active numerical metrics"

    async def fetch_data(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prior_start, prior_end = get_previous_period(start_date, end_date)

        # 1. Current Period Aggregations
        curr_query = (
            select(
                MetricRecord.name,
                func.count(MetricRecord.id).label("count"),
                func.sum(MetricRecord.value).label("sum"),
                func.avg(MetricRecord.value).label("avg"),
                func.min(MetricRecord.value).label("min"),
                func.max(MetricRecord.value).label("max"),
            )
            .where(MetricRecord.timestamp >= start_date)
            .where(MetricRecord.timestamp <= end_date)
            .group_by(MetricRecord.name)
        )
        curr_res = await session.execute(curr_query)
        curr_rows = curr_res.all()

        # 2. Prior Period Aggregations (for delta comparison)
        prior_query = (
            select(
                MetricRecord.name,
                func.sum(MetricRecord.value).label("sum"),
                func.avg(MetricRecord.value).label("avg"),
            )
            .where(MetricRecord.timestamp >= prior_start)
            .where(MetricRecord.timestamp <= prior_end)
            .group_by(MetricRecord.name)
        )
        prior_res = await session.execute(prior_query)
        prior_data = {row.name: row for row in prior_res.all()}

        metrics_summary = {}
        kpis = {}
        deltas = {}

        for row in curr_rows:
            name = row.name
            c_sum = float(row.sum or 0.0)
            c_avg = float(row.avg or 0.0)
            c_count = int(row.count or 0)
            c_min = float(row.min or 0.0)
            c_max = float(row.max or 0.0)

            # Calculate % change vs prior period
            pct_delta = 0.0
            if name in prior_data and prior_data[name].sum:
                p_sum = float(prior_data[name].sum)
                if p_sum != 0:
                    pct_delta = round(((c_sum - p_sum) / p_sum) * 100.0, 1)

            metrics_summary[name] = {
                "name": name,
                "count": c_count,
                "sum": c_sum,
                "avg": c_avg,
                "min": c_min,
                "max": c_max,
                "delta_pct": pct_delta,
            }
            kpis[name] = f"{c_sum:,.2f}" if c_sum > 100 else f"{c_sum:,.1f}"
            deltas[name] = pct_delta

        # 3. Daily time-series breakdown for top metrics (up to 4)
        top_metric_names = sorted(
            metrics_summary.keys(),
            key=lambda k: metrics_summary[k]["count"],
            reverse=True,
        )[:4]

        timeseries_data = defaultdict(lambda: defaultdict(float))
        if top_metric_names:
            ts_query = (
                select(
                    MetricRecord.name,
                    MetricRecord.timestamp,
                    MetricRecord.value,
                )
                .where(MetricRecord.timestamp >= start_date)
                .where(MetricRecord.timestamp <= end_date)
                .where(MetricRecord.name.in_(top_metric_names))
                .order_by(MetricRecord.timestamp.asc())
            )
            ts_res = await session.execute(ts_query)
            for m_name, ts, val in ts_res.all():
                day_str = ts.strftime("%Y-%m-%d")
                timeseries_data[m_name][day_str] += float(val)

        return {
            "metrics": metrics_summary,
            "kpis": kpis,
            "deltas": deltas,
            "top_metric_names": top_metric_names,
            "timeseries": dict(timeseries_data),
        }

    async def render_charts(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        charts: Dict[str, bytes] = {}
        top_names = data.get("top_metric_names", [])
        ts_data = data.get("timeseries", {})
        metrics = data.get("metrics", {})

        # 1. Primary Time-series Line Chart
        if top_names and ts_data:
            # Union of all dates
            all_dates = sorted(
                list(set(d for name in top_names for d in ts_data.get(name, {}).keys()))
            )
            if all_dates:
                series_dict = {}
                for name in top_names:
                    series_dict[name.replace("_", " ").title()] = [
                        ts_data.get(name, {}).get(d, 0.0) for d in all_dates
                    ]
                fig_ts = chart_builder.build_line_chart(
                    x_values=all_dates,
                    series=series_dict,
                    title="Key Metrics Trend Over Time",
                    x_title="Date",
                    y_title="Daily Aggregated Value",
                )
                charts["timeseries"] = chart_builder.fig_to_png(fig_ts)

        # 2. Metric Volume / Event Counts Bar Chart
        if metrics:
            sorted_by_count = sorted(metrics.values(), key=lambda m: m["count"], reverse=True)[:8]
            categories = [m["name"].replace("_", " ").title() for m in sorted_by_count]
            counts = [m["count"] for m in sorted_by_count]
            fig_bar = chart_builder.build_bar_chart(
                categories=categories,
                series={"Event Count": counts},
                title="Metric Ingestion Volume by Name",
                x_title="Metric",
                y_title="Total Events",
            )
            charts["volumes"] = chart_builder.fig_to_png(fig_bar)

        # 3. Primary KPI Badge Card
        if metrics:
            first_m = next(iter(metrics.values()))
            m_name = first_m["name"].replace("_", " ").title()
            val_str = f"{first_m['sum']:,.1f}"
            delta_val = first_m.get("delta_pct", 0.0)
            charts["preview_card"] = chart_builder.build_kpi_card_image(
                title=f"{m_name} (Total)",
                value_str=val_str,
                delta_str=f"{abs(delta_val):.1f}% vs prior period",
                is_positive=(delta_val >= 0),
                subtitle="OmniMetrics Hub",
            )

        return charts

    async def generate_pdf(
        self,
        data: Dict[str, Any],
        charts: Dict[str, bytes],
        ai_summary: Optional[str] = None,
    ) -> bytes:
        metrics = data.get("metrics", {})

        # Prepare KPI cards for template
        kpi_cards = []
        for m in list(metrics.values())[:4]:
            delta = m.get("delta_pct", 0.0)
            kpi_cards.append({
                "title": m["name"].replace("_", " ").title(),
                "value": f"{m['sum']:,.2f}" if m['sum'] > 100 else f"{m['sum']:,.1f}",
                "delta": f"{abs(delta):.1f}%",
                "is_positive": (delta >= 0),
                "subtitle": "vs prior period",
            })

        # Prepare charts for template
        chart_containers = []
        if "timeseries" in charts:
            chart_containers.append({
                "title": "Time-Series Trajectory",
                "image_base64": pdf_renderer.chart_bytes_to_base64(charts["timeseries"]),
                "description": "Daily aggregated values across primary business metrics.",
            })
        if "volumes" in charts:
            chart_containers.append({
                "title": "Ingestion Volume Breakdown",
                "image_base64": pdf_renderer.chart_bytes_to_base64(charts["volumes"]),
                "description": "Total event volume ingested per metric.",
            })

        # Prepare table
        table_rows = []
        for m in metrics.values():
            delta_str = f"{'+' if m['delta_pct'] >= 0 else ''}{m['delta_pct']:.1f}%"
            table_rows.append([
                m["name"],
                f"{m['count']:,}",
                f"{m['sum']:,.2f}",
                f"{m['avg']:,.2f}",
                f"{m['min']:,.2f}",
                f"{m['max']:,.2f}",
                delta_str,
            ])

        tables = [{
            "title": "Complete Metric Performance Matrix",
            "headers": ["Metric Name", "Events", "Sum", "Average", "Min", "Max", "Period Delta"],
            "rows": table_rows,
        }]

        context = {
            "report_title": self.display_name,
            "date_range_label": data.get("date_range_label", "Selected Window"),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "ai_summary": ai_summary,
            "kpis": kpi_cards,
            "charts": chart_containers,
            "tables": tables,
        }

        html = pdf_renderer.render_html("base_report.html", context)
        return await pdf_renderer.render_pdf(html)

    async def generate_excel(self, data: Dict[str, Any]) -> bytes:
        wb = excel_exporter.create_workbook()
        ws_overview = wb.active
        ws_overview.title = "Executive Overview"

        # 1. Title Block
        r = excel_exporter.add_title_block(
            ws_overview,
            title=self.display_name,
            subtitle=f"Period: {data.get('date_range_label', 'Selected Window')} • Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            start_row=1,
        )

        # 2. KPI Cards
        metrics = data.get("metrics", {})
        kpis_data = []
        for m in list(metrics.values())[:4]:
            delta = m.get("delta_pct", 0.0)
            kpis_data.append({
                "title": m["name"].replace("_", " ").title(),
                "value": f"{m['sum']:,.1f}",
                "delta": f"{abs(delta):.1f}%",
                "is_positive": (delta >= 0),
            })
        r = excel_exporter.add_kpi_cards(ws_overview, kpis_data, start_row=r)

        # 3. Main Summary Table
        headers = ["Metric Name", "Event Count", "Total Sum", "Average", "Min Value", "Max Value", "Period Delta %"]
        rows = [
            [
                m["name"],
                m["count"],
                m["sum"],
                m["avg"],
                m["min"],
                m["max"],
                m["delta_pct"] / 100.0,
            ]
            for m in metrics.values()
        ]
        num_formats = {
            2: "#,##0",
            3: "#,##0.00",
            4: "#,##0.00",
            5: "#,##0.00",
            6: "#,##0.00",
            7: "0.0%",
        }
        excel_exporter.add_table(ws_overview, headers, rows, start_row=r, number_formats=num_formats)

        return excel_exporter.to_bytes(wb)

    async def sync_gsheets(self, data: Dict[str, Any], spreadsheet_id: str) -> bool:
        metrics = data.get("metrics", {})
        headers = ["Metric Name", "Event Count", "Total Sum", "Average", "Min", "Max", "Period Delta %"]
        rows = [
            [
                m["name"],
                m["count"],
                round(m["sum"], 2),
                round(m["avg"], 2),
                round(m["min"], 2),
                round(m["max"], 2),
                f"{m['delta_pct']}%",
            ]
            for m in metrics.values()
        ]
        kpi_dict = {m["name"]: f"{m['sum']:,.2f}" for m in list(metrics.values())[:5]}
        return await gsheets_exporter.sync_data(
            spreadsheet_id=spreadsheet_id,
            sheet_title="Universal Metrics",
            headers=headers,
            rows=rows,
            kpis=kpi_dict,
        )

    def format_telegram_caption(
        self,
        data: Dict[str, Any],
        ai_summary: Optional[str] = None,
    ) -> str:
        metrics = data.get("metrics", {})
        label = data.get("date_range_label", "Selected Period")

        lines = [
            f"📊 <b>{self.display_name}</b>",
            f"🗓 <i>Period: {label}</i>",
            "",
            "<b>Key Metrics:</b>",
        ]

        for m in list(metrics.values())[:5]:
            delta = m.get("delta_pct", 0.0)
            arrow = "🟢 ▲" if delta >= 0 else "🔴 ▼"
            lines.append(
                f"• <b>{m['name'].replace('_', ' ').title()}</b>: <code>{m['sum']:,.1f}</code> ({arrow} {abs(delta):.1f}%)"
            )

        if ai_summary:
            lines.append("")
            lines.append("🧠 <b>Executive Briefing:</b>")
            lines.append(ai_summary)

        return "\n".join(lines)
