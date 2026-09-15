"""Dynamic inline keyboards for Telegram bot."""
from typing import List, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.reports.registry import report_registry


def get_reports_keyboard() -> InlineKeyboardMarkup:
    """Dynamically generate keyboard with all discovered report plugins."""
    reports = report_registry.list_reports()
    buttons: List[List[InlineKeyboardButton]] = []

    for report in reports:
        buttons.append([
            InlineKeyboardButton(
                text=report.display_name,
                callback_data=f"rep:sel:{report.report_id}",
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="⚠️ No Reports Found - Refresh",
                callback_data="rep:refresh",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_date_ranges_keyboard(report_id: str) -> InlineKeyboardMarkup:
    """Generate date range selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="⚡ Today", callback_data=f"rep:rng:{report_id}:today"),
            InlineKeyboardButton(text="📆 Yesterday", callback_data=f"rep:rng:{report_id}:yesterday"),
        ],
        [
            InlineKeyboardButton(text="🗓️ Last 7 Days", callback_data=f"rep:rng:{report_id}:last_7_days"),
            InlineKeyboardButton(text="📈 Last 30 Days", callback_data=f"rep:rng:{report_id}:last_30_days"),
        ],
        [
            InlineKeyboardButton(text="📊 This Month", callback_data=f"rep:rng:{report_id}:this_month"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back to Reports", callback_data="rep:back:reports"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_formats_keyboard(report_id: str, date_range: str) -> InlineKeyboardMarkup:
    """Generate export format selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text="⚡ Instant Card (PNG + Text)",
                callback_data=f"rep:gen:{report_id}:{date_range}:png",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📄 Full PDF Report",
                callback_data=f"rep:gen:{report_id}:{date_range}:pdf",
            ),
            InlineKeyboardButton(
                text="📊 Excel Workbook",
                callback_data=f"rep:gen:{report_id}:{date_range}:excel",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📑 Sync to Google Sheets",
                callback_data=f"rep:gen:{report_id}:{date_range}:gsheets",
            ),
            InlineKeyboardButton(
                text="🚀 All-in-One",
                callback_data=f"rep:gen:{report_id}:{date_range}:all",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Back to Date Ranges",
                callback_data=f"rep:sel:{report_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_refresh_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with refresh button."""
    buttons = [
        [InlineKeyboardButton(text="🔄 Re-run / Choose Another", callback_data="rep:back:reports")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
