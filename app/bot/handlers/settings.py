"""Settings and diagnostic inspection handlers for Telegram bot."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.metric import MetricRecord
from app.reports.registry import report_registry

router = Router()


@router.message(Command("settings"))
@router.message(Command("status"))
async def cmd_settings(message: Message):
    """Display system status, user authorization, and database metrics count."""
    user = message.from_user
    user_id = user.id if user else 0
    is_allowed = settings.is_telegram_user_allowed(user_id) or not settings.ALLOWED_TELEGRAM_USERS

    total_records = 0
    try:
        async with async_session_maker() as session:
            res = await session.execute(select(func.count(MetricRecord.id)))
            total_records = res.scalar_one_or_none() or 0
    except Exception:
        pass

    reports = report_registry.list_reports()

    text = (
        f"⚙️ <b>OmniMetrics Hub System Status</b>\n\n"
        f"• <b>Version</b>: <code>{settings.APP_VERSION}</code> ({settings.APP_ENV})\n"
        f"• <b>Database Records</b>: <code>{total_records:,}</code> metrics ingested\n"
        f"• <b>Active Plugins</b>: <code>{len(reports)}</code> discovered\n"
        f"• <b>AI Analyst Engine</b>: <code>{settings.AI_PROVIDER}</code>\n"
        f"• <b>PDF Engine</b>: <code>{settings.PDF_ENGINE}</code>\n\n"
        f"👤 <b>Your Session:</b>\n"
        f"• User ID: <code>{user_id}</code>\n"
        f"• Status: {'🟢 <b>Authorized</b>' if is_allowed else '🔴 <b>Unauthorized</b>'}\n"
    )
    await message.answer(text, parse_mode="HTML")
