"""Async HTTP client for MAX Messenger Platform API (https://platform-api2.max.ru)."""
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class MAXClient:
    """Production-ready asynchronous client for MAX Messenger Bot API."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.token = token or settings.MAX_BOT_TOKEN
        self.base_url = (base_url or settings.MAX_API_URL or "https://platform-api2.max.ru").rstrip("/")
        self._http_client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Lazily initialize shared httpx async client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                verify=False,
                trust_env=False,
                headers={
                    "Authorization": self.token or "",
                    "Accept": "application/json",
                },
            )
        return self._http_client

    async def close(self) -> None:
        """Close underlying HTTP client session."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def is_configured(self) -> bool:
        """Check if bot token is provided."""
        return bool(self.token and self.token != "your_max_bot_token_here")

    async def send_message(
        self,
        text: str,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        keyboard: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send a message to a MAX chat or user, optionally with inline keyboard or attachments."""
        if not self.is_configured():
            logger.warning("MAXClient: MAX_BOT_TOKEN is not configured; skipping send_message.")
            return None

        client = await self.get_client()
        params: Dict[str, Any] = {}
        if chat_id is not None:
            params["chat_id"] = chat_id
        elif user_id is not None:
            params["user_id"] = user_id
        else:
            logger.error("MAXClient: Either chat_id or user_id must be provided to send_message.")
            return None

        all_attachments = list(attachments or [])
        if keyboard:
            all_attachments.append(keyboard)

        payload: Dict[str, Any] = {"text": text}
        if all_attachments:
            payload["attachments"] = all_attachments

        url = f"{self.base_url}/messages"
        try:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"MAX API Error ({exc.response.status_code}) sending message: {exc.response.text}")
            return None
        except Exception as exc:
            logger.error(f"Failed sending message to MAX: {exc}")
            return None

    async def answer_callback(
        self,
        callback_id: str,
        text: Optional[str] = None,
    ) -> bool:
        """Acknowledge or respond to an inline button callback query."""
        if not self.is_configured() or not callback_id:
            return False

        client = await self.get_client()
        url = f"{self.base_url}/answers"
        params = {"callback_id": callback_id}
        payload = {"text": text or ""} if text else {}

        try:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning(f"MAXClient: answer_callback failed: {exc}")
            return False

    async def send_action(
        self,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: str = "typing",
    ) -> bool:
        """Send chat action indicator ('typing', 'upload_photo', 'upload_document')."""
        if not self.is_configured():
            return False

        target_id = chat_id if chat_id is not None else user_id
        if not target_id:
            return False

        client = await self.get_client()
        url = f"{self.base_url}/chats/{target_id}/actions"
        try:
            resp = await client.post(url, json={"action": action})
            return resp.status_code in (200, 204)
        except Exception:
            return False

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        file_type: str = "file",
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """Upload file or image to MAX platform and return attachment token."""
        if not self.is_configured():
            return None

        client = await self.get_client()
        init_url = f"{self.base_url}/uploads"
        try:
            # Step 1: Request upload slot
            init_resp = await client.post(init_url, params={"type": file_type})
            init_resp.raise_for_status()
            data = init_resp.json()

            upload_url = data.get("url") or data.get("upload_url")
            token = data.get("token")

            if not upload_url:
                logger.error(f"MAX uploads did not return upload_url: {data}")
                return None

            # Step 2: Upload actual binary data
            files = {"file": (filename, file_bytes, content_type)}
            up_resp = await client.post(upload_url, files=files)
            up_resp.raise_for_status()

            # Some endpoints return the token in the upload response
            if up_resp.headers.get("content-type", "").startswith("application/json"):
                up_data = up_resp.json()
                if "token" in up_data:
                    token = up_data["token"]

            return token
        except Exception as exc:
            logger.error(f"Failed uploading {file_type} '{filename}' to MAX: {exc}")
            return None

    async def send_document(
        self,
        file_bytes: bytes,
        filename: str,
        caption: str = "",
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upload and send document (PDF/Excel) to MAX chat."""
        token = await self.upload_file(file_bytes, filename, file_type="file")
        if not token:
            # If upload token isn't supported, send caption text with notification
            return await self.send_message(
                text=f"{caption}\n\n📎 <i>Файл '{filename}' сгенерирован (размер: {len(file_bytes):,} байт).</i>",
                chat_id=chat_id,
                user_id=user_id,
            )

        attachment = {
            "type": "file",
            "payload": {
                "token": token,
            },
        }
        return await self.send_message(
            text=caption,
            chat_id=chat_id,
            user_id=user_id,
            attachments=[attachment],
        )

    async def send_photo(
        self,
        photo_bytes: bytes,
        filename: str = "preview.png",
        caption: str = "",
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        keyboard: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upload and send photo (PNG card) to MAX chat."""
        token = await self.upload_file(photo_bytes, filename, file_type="image", content_type="image/png")
        attachments = []
        if token:
            attachments.append({
                "type": "image",
                "payload": {"token": token},
            })

        return await self.send_message(
            text=caption,
            chat_id=chat_id,
            user_id=user_id,
            keyboard=keyboard,
            attachments=attachments if attachments else None,
        )

    async def get_updates(
        self,
        marker: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Fetch pending events via Long Polling GET /updates."""
        if not self.is_configured():
            return []

        client = await self.get_client()
        url = f"{self.base_url}/updates"
        params: Dict[str, Any] = {"limit": limit}
        if marker is not None:
            params["marker"] = marker

        try:
            resp = await client.get(url, params=params, timeout=35.0)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data.get("updates", [])
            elif isinstance(data, list):
                return data
            return []
        except httpx.TimeoutException:
            return []
        except Exception as exc:
            logger.warning(f"Error fetching updates from MAX: {exc}")
            return []

    async def set_webhook(self, webhook_url: str) -> bool:
        """Register Webhook URL with MAX Messenger platform."""
        if not self.is_configured():
            return False

        client = await self.get_client()
        url = f"{self.base_url}/subscriptions"
        try:
            resp = await client.post(url, json={"url": webhook_url})
            resp.raise_for_status()
            logger.info(f"Successfully configured MAX Webhook URL: {webhook_url}")
            return True
        except Exception as exc:
            logger.error(f"Failed to set MAX Webhook: {exc}")
            return False

    async def delete_webhook(self) -> bool:
        """Remove active Webhook subscription."""
        if not self.is_configured():
            return False

        client = await self.get_client()
        url = f"{self.base_url}/subscriptions"
        try:
            resp = await client.delete(url)
            return resp.status_code in (200, 204)
        except Exception as exc:
            logger.warning(f"Failed to delete MAX Webhook: {exc}")
            return False


max_client = MAXClient()
