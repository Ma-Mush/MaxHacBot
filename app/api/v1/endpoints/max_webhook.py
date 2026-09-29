"""FastAPI Webhook endpoint for MAX Messenger platform events."""
import logging
from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, Request, Response, status

from app.max_bot.dispatcher import max_dispatcher

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", summary="MAX Messenger Webhook Receiver")
async def receive_max_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> Dict[str, str]:
    """Receive and asynchronously dispatch incoming updates from MAX Messenger."""
    try:
        payload = await request.json()
    except Exception as exc:
        logger.warning(f"Invalid JSON received on MAX webhook: {exc}")
        return {"status": "error", "message": "invalid_json"}

    update_type = payload.get("update_type", "unknown")
    logger.info(f"Received MAX webhook event: {update_type}")

    # Process in background task so MAX receives quick 200 OK
    background_tasks.add_task(max_dispatcher.handle_update, payload)
    return {"status": "ok"}


@router.get("", summary="MAX Messenger Webhook Verification")
async def verify_max_webhook() -> Dict[str, str]:
    """Health check for MAX webhook configuration."""
    return {"status": "active", "service": "MAX Messenger Webhook"}
