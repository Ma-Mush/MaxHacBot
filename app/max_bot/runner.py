"""MAX Messenger Bot runner for Long Polling and lifecycle execution."""
import asyncio
import logging
from typing import Optional

from app.core.config import settings
from app.core.database import close_db, init_db
from app.max_bot.client import max_client
from app.max_bot.dispatcher import max_dispatcher
from app.reports.registry import report_registry

logger = logging.getLogger(__name__)


async def run_max_bot() -> None:
    """Entrypoint to launch MAX Messenger Bot with long polling loop."""
    logger.info("Initializing OmniMetrics Hub for MAX Messenger...")
    await init_db()

    logger.info("Discovering report plugins...")
    report_registry.discover()
    logger.info(f"Loaded {len(report_registry.list_reports())} report plugins.")

    if not max_client.is_configured():
        logger.warning(
            "⚠️ MAX_BOT_TOKEN is not configured in .env!\n"
            "To connect to live MAX Messenger, obtain a token from https://dev.max.ru or @MasterBot.\n"
            "Running polling loop in standby mode."
        )

    logger.info("Starting MAX Messenger Bot event polling loop...")
    marker: Optional[int] = None
    running = True

    try:
        while running:
            try:
                if max_client.is_configured():
                    updates = await max_client.get_updates(marker=marker, limit=50)
                    for update in updates:
                        update_id = update.get("update_id") or update.get("timestamp")
                        if update_id and isinstance(update_id, int):
                            marker = max(marker or 0, update_id + 1)
                        await max_dispatcher.handle_update(update)

                    if not updates:
                        await asyncio.sleep(1.0)
                else:
                    await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                running = False
                break
            except Exception as exc:
                logger.error(f"Error in MAX polling iteration: {exc}")
                await asyncio.sleep(3.0)
    finally:
        await max_client.close()
        await close_db()
        logger.info("MAX Messenger Bot shutdown completed.")
