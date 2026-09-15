"""Telegram Bot runner and dispatcher configuration."""
import asyncio
import logging
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import reports, settings, start
from app.bot.middlewares.auth import WhitelistAuthMiddleware
from app.core.config import settings as app_settings
from app.core.database import close_db, init_db
from app.reports.registry import report_registry
from app.scheduler.jobs import setup_scheduler

logger = logging.getLogger(__name__)


def create_bot() -> Optional[Bot]:
    """Instantiate Bot instance if TELEGRAM_BOT_TOKEN is set."""
    if not app_settings.TELEGRAM_BOT_TOKEN or app_settings.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        return None
    return Bot(
        token=app_settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure Aiogram Dispatcher with middlewares and handlers."""
    dp = Dispatcher()

    # Register whitelist middleware
    auth_middleware = WhitelistAuthMiddleware()
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)

    # Register handler routers
    dp.include_router(start.router)
    dp.include_router(reports.router)
    dp.include_router(settings.router)

    return dp


async def run_bot() -> None:
    """Entrypoint to launch Telegram bot long-polling with background scheduler."""
    bot = create_bot()
    if not bot:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not configured! "
            "Set TELEGRAM_BOT_TOKEN in your .env file to enable the Telegram bot."
        )
        return

    logger.info("Initializing database...")
    await init_db()

    logger.info("Discovering report plugins...")
    report_registry.discover()
    logger.info(f"Discovered {len(report_registry.list_reports())} report plugins.")

    dp = create_dispatcher()

    # Start scheduler if enabled
    scheduler = None
    if app_settings.SCHEDULER_ENABLED:
        scheduler = setup_scheduler(bot)
        if scheduler:
            scheduler.start()
            logger.info("APScheduler background scheduler started.")

    try:
        logger.info("Starting Telegram Bot long-polling...")
        await dp.start_polling(bot)
    finally:
        if scheduler and scheduler.running:
            scheduler.shutdown()
        await bot.session.close()
        await close_db()
        logger.info("Telegram bot shutdown completed.")
