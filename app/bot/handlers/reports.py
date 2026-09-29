"""Interactive report generation and format delivery handlers for Telegram bot."""
from datetime import datetime
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards.inline import (
    get_date_ranges_keyboard,
    get_formats_keyboard,
    get_refresh_keyboard,
    get_reports_keyboard,
)
from app.core.database import async_session_maker
from app.core.date_utils import parse_date_range
from app.reports.engine import report_engine
from app.reports.registry import report_registry

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("report"))
async def cmd_report(message: Message):
    """Handle /report command showing available plugins."""
    await message.answer(
        "📊 <b>Select a Report Plugin:</b>\n"
        "Choose an analytics suite below to configure timeframe and format:",
        reply_markup=get_reports_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "rep:back:reports")
@router.callback_query(F.data == "rep:refresh")
async def cb_back_to_reports(callback: CallbackQuery):
    """Return to main reports menu."""
    report_registry.discover()
    await callback.message.edit_text(
        "📊 <b>Select a Report Plugin:</b>\n"
        "Choose an analytics suite below to configure timeframe and format:",
        reply_markup=get_reports_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rep:sel:"))
async def cb_select_report(callback: CallbackQuery):
    """User selected a report; prompt for date range."""
    parts = callback.data.split(":")
    report_id = parts[2]
    report = report_registry.get(report_id)

    if not report:
        await callback.answer(f"Report '{report_id}' not found.", show_alert=True)
        return

    text = (
        f"Selected: <b>{report.display_name}</b>\n"
        f"<i>{report.description}</i>\n\n"
        f"🗓 <b>Choose Date Range:</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_date_ranges_keyboard(report_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rep:rng:"))
async def cb_select_range(callback: CallbackQuery):
    """User selected date range; prompt for export format."""
    parts = callback.data.split(":")
    report_id = parts[2]
    date_range = parts[3]
    report = report_registry.get(report_id)

    if not report:
        await callback.answer(f"Report '{report_id}' not found.", show_alert=True)
        return

    range_labels = {
        "today": "Today",
        "yesterday": "Yesterday",
        "last_7_days": "Last 7 Days",
        "last_30_days": "Last 30 Days",
        "this_month": "This Month",
    }
    label = range_labels.get(date_range, date_range)

    text = (
        f"Report: <b>{report.display_name}</b>\n"
        f"Window: <b>{label}</b>\n\n"
        f"📦 <b>Select Desired Export Format:</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_formats_keyboard(report_id, date_range),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rep:gen:"))
async def cb_generate_report(callback: CallbackQuery):
    """Execute report generation and send artifacts to the user."""
    parts = callback.data.split(":")
    report_id = parts[2]
    date_range = parts[3]
    format_type = parts[4]

    report = report_registry.get(report_id)
    if not report:
        await callback.answer("Report plugin not found.", show_alert=True)
        return

    await callback.answer("⚙️ Generating report, please wait...")
    chat_id = callback.message.chat.id
    bot = callback.bot

    status_msg = await callback.message.answer(
        f"⏳ <i>Compiling {report.display_name} ({date_range})...</i>",
        parse_mode="HTML",
    )

    try:
        start_date, end_date = parse_date_range(date_range)
        date_label = date_range.replace("_", " ").title()

        # Map format_type to engine formats
        if format_type == "all":
            req_formats = ["png", "pdf", "excel"]
        elif format_type == "png":
            req_formats = ["png", "summary"]
        elif format_type == "pdf":
            req_formats = ["pdf", "png"]
        elif format_type == "excel":
            req_formats = ["excel"]
        elif format_type == "gsheets":
            req_formats = ["gsheets"]
        else:
            req_formats = [format_type]

        # Trigger chat action
        if format_type in ("png", "all"):
            await bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
        else:
            await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)

        async with async_session_maker() as session:
            generated = await report_engine.generate_report(
                report_id=report_id,
                start_date=start_date,
                end_date=end_date,
                date_range_label=date_label,
                formats=req_formats,
                session=session,
            )

        # 1. Deliver PNG preview / Card with rich caption
        if format_type in ("png", "all") or generated.primary_card_png:
            if generated.primary_card_png:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=BufferedInputFile(
                        generated.primary_card_png,
                        filename=f"{report_id}_preview.png",
                    ),
                    caption=generated.telegram_caption,
                    parse_mode="HTML",
                )
            elif generated.telegram_caption:
                await bot.send_message(
                    chat_id=chat_id,
                    text=generated.telegram_caption,
                    parse_mode="HTML",
                )

        # 2. Deliver PDF if requested
        if format_type in ("pdf", "all") and generated.pdf_bytes:
            await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            date_str = start_date.strftime("%Y%m%d")
            await bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(
                    generated.pdf_bytes,
                    filename=f"{report_id}_{date_str}.pdf",
                ),
                caption=f"📄 <b>PDF Report</b>: {report.display_name}",
                parse_mode="HTML",
            )

        # 3. Deliver Excel if requested
        if format_type in ("excel", "all") and generated.excel_bytes:
            await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            date_str = start_date.strftime("%Y%m%d")
            await bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(
                    generated.excel_bytes,
                    filename=f"{report_id}_{date_str}.xlsx",
                ),
                caption=f"📊 <b>Excel Workbook</b>: {report.display_name}",
                parse_mode="HTML",
            )

        # 4. Confirm Google Sheets sync
        if format_type == "gsheets":
            if generated.gsheets_synced:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ <b>Google Sheets Synchronized!</b>\nMetrics successfully synced to your designated sheet.",
                    parse_mode="HTML",
                )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text="⚠️ <b>Google Sheets Notice</b>\nSync skipped or failed. Verify that your service account JSON credentials and spreadsheet ID are configured in <code>.env</code>.",
                    parse_mode="HTML",
                )

        # Remove temporary status message
        await status_msg.delete()

    except Exception as exc:
        logger.error(f"Error generating report for Telegram: {exc}", exc_info=True)
        await status_msg.edit_text(
            f"❌ <b>Report Generation Failed</b>\n<code>{str(exc)}</code>",
            parse_mode="HTML",
            reply_markup=get_refresh_keyboard(),
        )
