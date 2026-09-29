"""Keyboard and interactive button builders for MAX Messenger Bot."""
from typing import Any, Dict, List
from app.reports.registry import report_registry


def create_callback_button(text: str, payload: str) -> Dict[str, Any]:
    """Build a single callback button conforming to MAX Bot API."""
    return {
        "type": "callback",
        "text": text,
        "payload": payload,
    }


def create_link_button(text: str, url: str) -> Dict[str, Any]:
    """Build a URL link button conforming to MAX Bot API."""
    return {
        "type": "link",
        "text": text,
        "url": url,
    }


def build_keyboard_attachment(rows: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Wrap rows of buttons into MAX inline_keyboard attachment."""
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": rows,
        },
    }


def get_max_reports_keyboard() -> Dict[str, Any]:
    """Build inline keyboard listing all available report plugins."""
    reports = report_registry.list_reports()
    rows: List[List[Dict[str, Any]]] = []

    for report in reports:
        rows.append([create_callback_button(report.display_name, f"rep:sel:{report.report_id}")])

    rows.append([create_callback_button("🟣 Синхронизировать Wildberries", "rep:sync:wb")])
    rows.append([create_callback_button("🔄 Обновить список плагинов", "rep:refresh")])
    return build_keyboard_attachment(rows)


def get_max_date_ranges_keyboard(report_id: str) -> Dict[str, Any]:
    """Build inline keyboard with timeframe options for a selected report."""
    rows: List[List[Dict[str, Any]]] = [
        [
            create_callback_button("⚡ Сегодня", f"rep:rng:{report_id}:today"),
            create_callback_button("📆 Вчера", f"rep:rng:{report_id}:yesterday"),
        ],
        [
            create_callback_button("🗓️ Последние 7 дней", f"rep:rng:{report_id}:last_7_days"),
            create_callback_button("📈 Последние 30 дней", f"rep:rng:{report_id}:last_30_days"),
        ],
        [
            create_callback_button("📊 Текущий месяц", f"rep:rng:{report_id}:this_month"),
        ],
        [
            create_callback_button("⬅️ Назад к списку отчетов", "rep:back:reports"),
        ],
    ]
    return build_keyboard_attachment(rows)


def get_max_formats_keyboard(report_id: str, date_range: str) -> Dict[str, Any]:
    """Build inline keyboard for export format selection."""
    rows: List[List[Dict[str, Any]]] = [
        [
            create_callback_button("⚡ Экспресс-сводка (PNG + Текст)", f"rep:gen:{report_id}:{date_range}:png"),
        ],
        [
            create_callback_button("📄 Корпоративный PDF-отчет", f"rep:gen:{report_id}:{date_range}:pdf"),
            create_callback_button("📊 Книга Excel (.xlsx)", f"rep:gen:{report_id}:{date_range}:excel"),
        ],
        [
            create_callback_button("🚀 Всё сразу (All-in-One)", f"rep:gen:{report_id}:{date_range}:all"),
        ],
        [
            create_callback_button("⬅️ Назад к выбору периода", f"rep:sel:{report_id}"),
        ],
    ]
    return build_keyboard_attachment(rows)


def get_max_refresh_keyboard() -> Dict[str, Any]:
    """Simple keyboard to return to main menu or trigger sync."""
    return build_keyboard_attachment([
        [create_callback_button("🟣 Синхронизировать Wildberries", "rep:sync:wb")],
        [create_callback_button("📊 Вернуться в меню отчетов", "rep:back:reports")],
    ])
