"""Start and help handlers for Telegram bot."""
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot.keyboards.inline import get_reports_keyboard
from app.core.config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command with an executive welcome and report catalog."""
    user_name = message.from_user.first_name if message.from_user else "Leader"
    text = (
        f"👋 <b>Welcome to {settings.APP_NAME}, {user_name}!</b>\n\n"
        f"OmniMetrics Hub ingests your business telemetry and compiles executive-grade "
        f"visual reports, PDFs, Excel workbooks, and AI briefings.\n\n"
        f"🚀 <b>Quick Commands:</b>\n"
        f"• /report — Browse reports and generate instant exports\n"
        f"• /settings — Inspect system configuration & your user ID\n"
        f"• /help — Show command reference\n\n"
        f"Select a report below to begin:"
    )
    await message.answer(text, reply_markup=get_reports_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    text = (
        f"📖 <b>OmniMetrics Bot Reference</b>\n\n"
        f"• <b>/report</b>: Select any registered report plugin, choose a time window (Today, Yesterday, Last 7/30 Days), and export as:\n"
        f"  - ⚡ Instant PNG Card + Rich Summary\n"
        f"  - 📄 Headless Styled PDF\n"
        f"  - 📊 Multi-tab Formatted Excel (.xlsx)\n"
        f"  - 📑 Live Google Sheets Sync\n\n"
        f"• <b>/settings</b>: View database and user permissions.\n"
        f"• <b>/status</b>: Quick health check of API and workers."
    )
    await message.answer(text, parse_mode="HTML")
