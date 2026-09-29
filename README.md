# 📊 OmniMetrics Hub: MAX Messenger & Telegram AI Business Hub

> **A self-hosted, production-ready, extensible business metrics hub and automated reporting engine delivered directly to the MAX Messenger platform and Telegram.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![MAX Bot API](https://img.shields.io/badge/MAX%20Bot%20API-platform--api2-blue.svg)](https://dev.max.ru)
[![Aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blue.svg)](https://docs.aiogram.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

**OmniMetrics Hub** empowers any business, engineering team, or solo developer to self-host their own analytics platform with a single command (`docker compose up`). Ingest arbitrary numerical metrics via a universal REST API, and generate high-impact reports—**styled executive PDFs**, **multi-tab Excel workbooks**, **live Google Sheets sync**, **standalone PNG preview cards**, and **AI-powered executive summaries**—delivered directly to your private **MAX Messenger** chats and Telegram channels on demand or on an automated schedule.

```
       ┌────────────────────────────────────────────────────────┐
       │             Universal Ingestion REST API               │
       │    POST /api/v1/metrics  •  POST /api/v1/metrics/batch │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │        PostgreSQL (JSONB) / SQLite Telemetry Store     │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │       Pluggable Report Architecture (BaseReport)       │
       │   • Universal Metrics Overview   • E-Commerce Briefing │
       │   • Custom User Plugins (app/custom_reports/*.py)      │
       └─────┬──────────────┬──────────────┬──────────────┬─────┘
             │              │              │              │
             ▼              ▼              ▼              ▼
       ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
       │ Headless  │  │ Corporate │  │ Standalone│  │ AI Brief  │
       │ Modern PDF│  │   Excel   │  │ High-DPI  │  │ Executive │
       │(WeasyPrint│  │ (.xlsx)   │  │ PNG Cards │  │ (LLM/Rule)│
       └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
             │              │              │              │
             └──────────────┼──────────────┴──────────────┘
                            ▼
       ┌────────────────────────────────────────────────────────┐
       │      Interactive MAX Messenger & Telegram Bots         │
       │    • MAX Bot API (Webhook + Polling) • Aiogram 3.x     │
       │    • Whitelist Security     • Dynamic Inline Menus     │
       │    • Date Range Pickers     • Automated APScheduler    │
       └────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Architectural Features

1. **Universal Ingestion Model**:
   - Accepts *any* numerical metric with arbitrary key-value dimensional tags (e.g. `{"region": "EU", "channel": "google_ads", "store_id": "42"}`) without requiring database schema migrations.
   - High-throughput batch ingestion supporting up to 5,000 metrics per request.
   - Protected by simple token header authentication (`X-API-Key`).

2. **Pluggable Report Strategy Pattern**:
   - Add new reports simply by dropping a Python file into `app/custom_reports/` subclassing `BaseReport`.
   - Dynamic discovery registers plugins automatically on startup—no boilerplate or core code changes.

3. **Intelligent Multi-Format Exporters**:
   - **Modern PDF**: Responsive executive layouts styled with CSS print media queries, embedded high-DPI charts, KPI badge blocks, and page numbering compiled via WeasyPrint or Playwright.
   - **Professional Excel (.xlsx)**: Generated with `openpyxl` containing dark slate corporate headers, zebra-striped data tables, auto-fitted columns, formatted currency (`$#,##0.00`) and percentages (`0.0%`), plus embedded chart images.
   - **Google Sheets Sync**: Direct synchronization to live Google Spreadsheets using Google Service Account credentials.
   - **Executive PNG Previews**: Standalone visual KPI badges and chart cards formatted for instant mobile viewing.

4. **Smart Visualizations & AI Insights**:
   - **Auto-Chart Heuristics**: Time-series $\to$ Line/Area; Categorical $\to$ Grouped Bar/Donut; KPIs $\to$ Delta Badges. Dual-engine Plotly with automatic Matplotlib fallback.
   - **AI Executive Briefing**: Multi-provider support (OpenAI `gpt-4o-mini`, Anthropic `claude-3-5-sonnet`, local Ollama `llama3`, and zero-dependency rule-based heuristics) delivering structured 4-bullet executive summaries (🚀 Key Gain, ⚠️ Drop/Friction, 🔍 Anomaly, 🎯 Recommended Action).

5. **Telegram Bot (Aiogram 3.x) & Scheduler**:
   - Whitelist middleware enforcing access solely to IDs in `ALLOWED_TELEGRAM_USERS`.
   - Dynamic inline keyboards populated straight from `ReportRegistry.list_reports()`.
   - Date range selector: *Today*, *Yesterday*, *Last 7 Days*, *Last 30 Days*, *This Month*.
   - Format toggles: *Instant Card (PNG + Text)*, *Full PDF Report*, *Excel Workbook*, *Google Sheets Sync*, or *All-in-One*.
   - Automated `APScheduler` background cron jobs for scheduled daily/weekly executive dispatches.

6. **Complete Developer CLI**:
   - Seed realistic demo data, test reports locally without Telegram, and scaffold new plugins in seconds.

---

## 🚀 Quickstart with Docker Compose

Deploy the entire production stack (PostgreSQL + FastAPI Ingestion API + Telegram Bot & Scheduler) in 60 seconds:

### 1. Clone & Configure Environment

```bash
git clone https://github.com/your-org/omni-metrics.git
cd omni-metrics
cp .env.example .env
```

Edit `.env`:
```env
APP_API_KEY="your_secure_api_key_here"
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
ALLOWED_TELEGRAM_USERS="123456789"
```

### 2. Start Services

```bash
docker compose up -d --build
```

- **FastAPI Documentation**: Open `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`
- **Telegram Bot**: Open Telegram, search for your bot, and send `/start`!

---

## 🛠️ Local Development Setup

If running locally without Docker:

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure local environment
cp .env.example .env
# By default, .env uses SQLite (sqlite+aiosqlite:///./omni_metrics.db)

# 4. Seed 60 days of realistic demo telemetry
python cli.py seed-demo --days 60

# 5. Run the FastAPI REST service
python cli.py run-api --port 8000 --reload

# 6. (Optional) Run the Telegram Bot
python cli.py run-bot
```

---

## 📡 Universal REST Ingestion API

All endpoints require the `X-API-Key` header matching `APP_API_KEY` in `.env`.

### 1. Ingest a Single Metric

```bash
curl -X POST "http://localhost:8000/api/v1/metrics" \
  -H "X-API-Key: omni_test_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "revenue",
    "value": 1250.50,
    "unit": "USD",
    "tags": {
      "channel": "google_ads",
      "region": "US",
      "store_id": "flagship-01"
    }
  }'
```

### 2. Ingest Batch Metrics (Up to 5,000 per request)

```bash
curl -X POST "http://localhost:8000/api/v1/metrics/batch" \
  -H "X-API-Key: omni_test_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {
        "name": "revenue",
        "value": 450.00,
        "unit": "USD",
        "tags": {"channel": "direct", "region": "EU"}
      },
      {
        "name": "orders_count",
        "value": 5,
        "unit": "pcs",
        "tags": {"channel": "direct", "region": "EU"}
      },
      {
        "name": "api_latency_ms",
        "value": 48.2,
        "unit": "ms",
        "tags": {"host": "prod-api-01"}
      }
    ]
  }'
```

### 3. Discover Available Metric Names & Tag Keys

```bash
curl -X GET "http://localhost:8000/api/v1/metrics/meta" \
  -H "X-API-Key: omni_test_secret_key"
```

**Response:**
```json
{
  "metric_names": ["api_latency_ms", "cpu_utilization", "orders_count", "refunds", "revenue", "visitors"],
  "tag_keys": ["channel", "host", "region", "source"],
  "total_records": 1587
}
```

### 4. Direct Download Report File via API (PDF / Excel / PNG)

```bash
# Download Styled PDF
curl -X GET "http://localhost:8000/api/v1/reports/ecommerce_summary/download?format=pdf&date_range=last_7_days" \
  -H "X-API-Key: omni_test_secret_key" \
  -o weekly_report.pdf

# Download Formatted Excel Workbook
curl -X GET "http://localhost:8000/api/v1/reports/ecommerce_summary/download?format=excel&date_range=last_7_days" \
  -H "X-API-Key: omni_test_secret_key" \
  -o weekly_report.xlsx
```

---

## 🤖 Telegram Bot Interface

### Security Whitelist
The bot is protected by `WhitelistAuthMiddleware`. Only user IDs listed in `ALLOWED_TELEGRAM_USERS` can trigger actions. Non-whitelisted users receive a prompt displaying their numeric Telegram User ID to provide to the administrator.

### Interactive Bot Workflow
1. **/start** or **/report**: Renders an inline keyboard dynamically showing all registered report plugins.
2. **Select Date Window**:
   - ⚡ Today
   - 📆 Yesterday
   - 🗓️ Last 7 Days
   - 📈 Last 30 Days
   - 📊 This Month
3. **Select Format**:
   - ⚡ Instant Card (PNG preview + rich Telegram caption)
   - 📄 Full PDF Report (document attachment)
   - 📊 Excel Workbook (.xlsx attachment with embedded charts and formulas)
   - 📑 Sync to Google Sheets
   - 🚀 All-in-One (sends all formats in a single request)

---

## 🤖 MAX Messenger Bot (Мессенджер МАКС)

OmniMetrics Hub fully supports native integration with the **MAX Messenger Platform** (`https://platform-api2.max.ru`), enabling corporate teams and business owners to receive real-time telemetry, run factor analysis, and request executive briefings directly in MAX.

### 1. Configuration in `.env`
```env
MAX_BOT_TOKEN="your_max_bot_token_here"
MAX_API_URL="https://platform-api2.max.ru"
ALLOWED_MAX_USERS=""  # Leave empty for open access or specify user IDs
```

### 2. Run Modes
- **Long Polling (Development / Testing)**:
  ```bash
  python cli.py run-max-bot
  ```
- **Production Webhook (FastAPI)**:
  Set your webhook in MAX to:
  `https://your-domain.com/api/v1/max/webhook`
  All incoming `bot_started`, `message_created`, and `message_callback` events are dispatched asynchronously.

### 3. Interactive Bot Features in MAX
- **Interactive Inline Keyboards**: Dynamic selection of reports (`ReportRegistry`), date ranges (*Сегодня, Вчера, 7 дней, 30 дней*), and format toggles.
- **Rich Executive Cards & Charts**: Instant Plotly PNG preview cards uploaded directly to MAX chats via `POST /uploads`.
- **Corporate Documents**: Full multi-page PDF briefings and Excel spreadsheets delivered as native file attachments.
- **Security Whitelist**: Access control via `ALLOWED_MAX_USERS` and instant status monitoring via `/status`.

---

## 🧩 How to Write a Custom Report in 10 Minutes

The pluggable report architecture uses the Strategy Pattern. Adding a report requires **no database migrations** and **no changes to the bot UI**.

### Step 1: Scaffold the Plugin
Run the CLI scaffolding command:

```bash
python cli.py create-plugin saas_metrics
```

This creates `app/custom_reports/saas_metrics_report.py`.

### Step 2: Implement the Report Class

```python
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import MetricRecord
from app.reports.base import BaseReport
from app.services.chart_builder import chart_builder
from app.services.excel_exporter import excel_exporter
from app.services.pdf_renderer import pdf_renderer


class SaasMetricsReport(BaseReport):
    report_id = "saas_metrics"
    display_name = "🚀 SaaS Growth & Churn Overview"
    description = "MRR growth, churn rate, active subscriptions, and ARPU"

    async def fetch_data(self, session: AsyncSession, start_date: datetime, end_date: datetime, **kwargs) -> Dict[str, Any]:
        # Query metrics from the universal MetricRecord table
        q = select(MetricRecord.name, func.sum(MetricRecord.value)).where(
            MetricRecord.timestamp >= start_date, MetricRecord.timestamp <= end_date
        ).group_by(MetricRecord.name)
        res = await session.execute(q)
        totals = dict(res.all())
        
        return {
            "mrr": totals.get("mrr", 24500.0),
            "churn_rate": totals.get("churn_rate", 2.1),
            "kpis": {"MRR": f"${totals.get('mrr', 24500):,.2f}", "Churn": "2.1%"},
            "deltas": {"mrr": 8.4, "churn_rate": -0.3},
        }

    async def render_charts(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        # Generate chart PNGs
        preview = chart_builder.build_kpi_card_image(
            title="Monthly Recurring Revenue",
            value_str=f"${data.get('mrr', 0):,.0f}",
            delta_str="8.4% growth",
            is_positive=True,
            subtitle="SaaS Growth",
        )
        return {"preview_card": preview}

    async def generate_pdf(self, data: Dict[str, Any], charts: Dict[str, bytes], ai_summary: Optional[str] = None) -> bytes:
        context = {
            "report_title": self.display_name,
            "date_range_label": data.get("date_range_label", "Selected Period"),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "ai_summary": ai_summary,
            "kpis": [{"title": "MRR", "value": f"${data.get('mrr', 0):,.2f}", "delta": "8.4%", "is_positive": True}],
            "charts": [],
            "tables": [],
        }
        html = pdf_renderer.render_html("base_report.html", context)
        return await pdf_renderer.render_pdf(html)

    async def generate_excel(self, data: Dict[str, Any]) -> bytes:
        wb = excel_exporter.create_workbook()
        ws = wb.active
        ws.title = "SaaS Metrics"
        excel_exporter.add_title_block(ws, "SaaS Performance Ledger")
        excel_exporter.add_table(ws, ["Metric", "Value"], [["MRR", data.get("mrr", 0)], ["Churn %", data.get("churn_rate", 0)]])
        return excel_exporter.to_bytes(wb)

    def format_telegram_caption(self, data: Dict[str, Any], ai_summary: Optional[str] = None) -> str:
        lines = [
            f"🚀 <b>{self.display_name}</b>",
            f"• 💰 <b>MRR</b>: <code>${data.get('mrr', 0):,.2f}</code>",
            f"• 📉 <b>Churn</b>: <code>{data.get('churn_rate', 0)}%</code>",
        ]
        if ai_summary:
            lines.append(f"\n🧠 <b>AI Briefing:</b>\n{ai_summary}")
        return "\n".join(lines)
```

### Step 3: Verify Locally
Test your new report immediately without needing Telegram:

```bash
python cli.py test-report saas_metrics --days 7
```

All artifacts (`.pdf`, `.xlsx`, `.png`, and caption) will be generated into `./output/`!

---

## 💻 CLI Reference

| Command | Description |
|---|---|
| `python cli.py sync-wb [--days 14] [--mock]` | Synchronize sales and returns directly from Wildberries Statistics API / sandbox |
| `python cli.py sync-ozon [--days 14] [--mock]` | Synchronize postings and revenue directly from Ozon Seller API / sandbox |
| `python cli.py sync-yandex [--days 14] [--mock]` | Synchronize orders and sales directly from Yandex Market Partner API / sandbox |
| `python cli.py seed-demo [--days 60]` | Seed historical e-commerce and server metrics |
| `python cli.py list-reports` | List all registered and discovered plugins |
| `python cli.py test-report <report_id> [--days 7]` | Generate PDF, Excel, and PNG artifacts into `./output/` |
| `python cli.py create-plugin <name>` | Scaffold a new report plugin in `app/custom_reports/` |
| `python cli.py run-api` | Launch FastAPI web server |
| `python cli.py run-max-bot` | Launch MAX Messenger Bot polling runner |
| `python cli.py run-bot` | Launch Telegram bot long-polling with scheduler |
| `python cli.py run-all` | Run API, MAX Bot, and Telegram bot concurrently |

---

## 🛒 Marketplace Connectors (Wildberries, Ozon & Yandex.Маркет)

OmniMetrics Hub features native integrations with major Russian e-commerce marketplaces:

### 1. Wildberries Statistics API
- **Endpoint**: `https://statistics-api.wildberries.ru/api/v1/supplier/sales`
- **CLI**: `python cli.py sync-wb [--days 14] [--mock]`
- **MAX Bot**: `/wb` or button `🟣 Синхронизировать Wildberries`
- **REST**: `POST /api/v1/connectors/wildberries/sync`, `GET /api/v1/connectors/wildberries/status`

### 2. Ozon Seller API
- **Endpoint**: `https://api-seller.ozon.ru/v3/posting/fbs/list`
- **CLI**: `python cli.py sync-ozon [--days 14] [--mock]`
- **MAX Bot**: `/ozon` or button `🔵 Синхронизировать Ozon`
- **REST**: `POST /api/v1/connectors/ozon/sync`, `GET /api/v1/connectors/ozon/status`
- **Key Capabilities**: Pulls FBS/FBO shipments, cluster delivery logistics, fulfillment warehouse metrics, and financial reconciliations.

### 3. Yandex Market Partner API
- **Endpoint**: `https://api.partner.market.yandex.ru/campaigns/{campaign_id}/orders`
- **CLI**: `python cli.py sync-yandex [--days 14] [--mock]`
- **MAX Bot**: `/yandex` or button `🟡 Синхронизировать Яндекс.Маркет`
- **REST**: `POST /api/v1/connectors/yandex-market/sync`, `GET /api/v1/connectors/yandex-market/status`
- **Fail-Safe Sandbox**: Fully functional mock dataset generation for instant live jury testing across all channels.

---

## 🧪 Running Tests

OmniMetrics Hub comes with an automated pytest suite covering endpoints, reporting plugins, calculations, and exporters:

```bash
pytest -v
```

---

## 📄 License

This project is licensed under the **MIT License**. Free for commercial and private use.
