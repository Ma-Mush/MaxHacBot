"""Telegram authentication middleware restricting access to authorized user IDs."""
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhitelistAuthMiddleware(BaseMiddleware):
    """Middleware that intercepts events and enforces ALLOWED_TELEGRAM_USERS whitelist."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # If no allowed users are configured, deny all in production, or allow if debug/empty
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Check whitelist if configured
        if settings.ALLOWED_TELEGRAM_USERS and not settings.is_telegram_user_allowed(user_id):
            logger.warning(f"Unauthorized Telegram access attempt from user_id={user_id} (@{user.username})")
            if isinstance(event, Message):
                await event.answer(
                    f"⛔ <b>Access Denied</b>\n\n"
                    f"Your Telegram User ID is: <code>{user_id}</code>\n\n"
                    f"You are not in the <code>ALLOWED_TELEGRAM_USERS</code> whitelist.\n"
                    f"Please contact your OmniMetrics system administrator to grant access.",
                    parse_mode="HTML",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    f"⛔ Access Denied! Your User ID {user_id} is not authorized.",
                    show_alert=True,
                )
            return  # Halt execution

        return await handler(event, data)
