"""Automated scheduled report execution and delivery using APScheduler."""
import logging
from typing import List, Optional
from aiogram import Bot
from aiogram.types import BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.date_utils import parse_date_range
from app.reports.engine import report_engine
from app.reports.registry import report_registry

logger = logging.getLogger(__name__)


async def dispatch_scheduled_report(
    bot: Bot,
    report_id: str,
    date_range: str = "yesterday",
    chat_ids: Optional[List[int]] = None,
    formats: Optional[List[str]] = None,
) -> None:
    """Generate a scheduled report and broadcast it to target chat IDs."""
    if chat_ids is None:
        if settings.DEFAULT_SCHEDULED_CHAT_ID:
            chat_ids = [settings.DEFAULT_SCHEDULED_CHAT_ID]
        else:
            chat_ids = settings.ALLOWED_TELEGRAM_USERS

    if not chat_ids:
        logger.warning(f"Scheduled report '{report_id}' skipped: no target chat IDs configured.")
        return

    report = report_registry.get(report_id)
    if not report:
        logger.error(f"Scheduled report failed: plugin '{report_id}' not found.")
        return

    logger.info(f"Triggering scheduled dispatch for '{report_id}' to {len(chat_ids)} chats...")

    try:
        start_date, end_date = parse_date_range(date_range)
        date_label = date_range.replace("_", " ").title()
        req_formats = formats or ["png", "pdf", "excel"]

        async with async_session_maker() as session:
            generated = await report_engine.generate_report(
                report_id=report_id,
                start_date=start_date,
                end_date=end_date,
                date_range_label=date_label,
                formats=req_formats,
                session=session,
            )

        for chat_id in chat_ids:
            try:
                # 1. Send Preview photo + Caption
                if generated.primary_card_png:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=BufferedInputFile(generated.primary_card_png, filename="preview.png"),
                        caption=f"⏰ <b>Scheduled Briefing</b>\n\n{generated.telegram_caption}",
                        parse_mode="HTML",
                    )
                elif generated.telegram_caption:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"⏰ <b>Scheduled Briefing</b>\n\n{generated.telegram_caption}",
                        parse_mode="HTML",
                    )

                # 2. Send PDF
                if "pdf" in req_formats and generated.pdf_bytes:
                    date_str = start_date.strftime("%Y%m%d")
                    await bot.send_document(
                        chat_id=chat_id,
                        document=BufferedInputFile(generated.pdf_bytes, filename=f"{report_id}_{date_str}.pdf"),
                        caption=f"📄 Scheduled PDF: {report.display_name}",
                        parse_mode="HTML",
                    )

                # 3. Send Excel
                if "excel" in req_formats and generated.excel_bytes:
                    date_str = start_date.strftime("%Y%m%d")
                    await bot.send_document(
                        chat_id=chat_id,
                        document=BufferedInputFile(generated.excel_bytes, filename=f"{report_id}_{date_str}.xlsx"),
                        caption=f"📊 Scheduled Excel: {report.display_name}",
                        parse_mode="HTML",
                    )

                logger.info(f"Successfully dispatched scheduled report to chat_id={chat_id}")
            except Exception as exc:
                logger.error(f"Failed sending scheduled report to chat_id={chat_id}: {exc}")

    except Exception as exc:
        logger.error(f"Error during scheduled report execution for '{report_id}': {exc}", exc_info=True)


def setup_scheduler(bot: Bot) -> Optional[AsyncIOScheduler]:
    """Configure APScheduler with configured cron jobs."""
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Morning Report Job
    cron_expr = settings.CRON_MORNING_REPORT
    if cron_expr:
        try:
            parts = cron_expr.strip().split()
            if len(parts) == 5:
                minute, hour, day, month, day_of_week = parts
                trigger = CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                    timezone="UTC",
                )
                scheduler.add_job(
                    dispatch_scheduled_report,
                    trigger=trigger,
                    kwargs={
                        "bot": bot,
                        "report_id": settings.DEFAULT_SCHEDULED_REPORT_ID,
                        "date_range": "yesterday",
                    },
                    id="morning_executive_report",
                    name="Morning Executive Report",
                    replace_existing=True,
                )
                logger.info(f"Scheduled morning report job with cron: '{cron_expr}' (UTC)")
            else:
                logger.warning(f"Invalid cron expression '{cron_expr}'. Expected 5 space-separated parts.")
        except Exception as exc:
            logger.error(f"Failed to configure morning report cron job: {exc}")

    return scheduler
