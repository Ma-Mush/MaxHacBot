"""Google Sheets sync service using Google Service Account authentication."""
import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GSheetsExporterService:
    """Service to push and synchronize report metrics to Google Sheets."""

    def __init__(self) -> None:
        self._service = None

    def _get_credentials(self) -> Any:
        """Load Google Service Account credentials from JSON string or file."""
        from google.oauth2 import service_account

        # 1. Check raw JSON env variable
        if settings.GSHEETS_SERVICE_ACCOUNT_JSON:
            raw = settings.GSHEETS_SERVICE_ACCOUNT_JSON.strip()
            # Check if base64 encoded
            if raw.startswith("{"):
                info = json.loads(raw)
            else:
                try:
                    decoded = base64.b64decode(raw).decode("utf-8")
                    info = json.loads(decoded)
                except Exception:
                    info = json.loads(raw)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

        # 2. Check service account file path
        sa_file = settings.GSHEETS_SERVICE_ACCOUNT_FILE
        if sa_file and os.path.exists(sa_file):
            return service_account.Credentials.from_service_account_file(sa_file, scopes=SCOPES)

        return None

    def _get_sheets_client(self) -> Any:
        """Initialize Google Sheets API client."""
        if self._service is not None:
            return self._service

        creds = self._get_credentials()
        if not creds:
            logger.warning(
                "Google Sheets credentials not configured. "
                "Set GSHEETS_SERVICE_ACCOUNT_FILE or GSHEETS_SERVICE_ACCOUNT_JSON."
            )
            return None

        from googleapiclient.discovery import build

        self._service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        return self._service

    async def sync_data(
        self,
        spreadsheet_id: str,
        sheet_title: str,
        headers: List[str],
        rows: List[List[Any]],
        kpis: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Synchronize tabular metrics and KPI summary to designated Google Spreadsheet."""
        client = self._get_sheets_client()
        if not client:
            return False

        try:
            # 1. Check if sheet exists or create it
            sheet_meta = client.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            existing_sheets = [s["properties"]["title"] for s in sheet_meta.get("sheets", [])]

            if sheet_title not in existing_sheets:
                add_sheet_body = {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": sheet_title,
                                    "gridProperties": {"rowCount": 1000, "columnCount": max(len(headers) + 2, 10)},
                                }
                            }
                        }
                    ]
                }
                client.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, body=add_sheet_body
                ).execute()

            # 2. Prepare content rows
            payload_values: List[List[Any]] = []

            # KPI section if present
            if kpis:
                payload_values.append(["EXECUTIVE KPI SUMMARY", ""])
                for k, v in kpis.items():
                    payload_values.append([k.replace("_", " ").title(), str(v)])
                payload_values.append([])  # Blank row

            # Main table headers & rows
            payload_values.append(headers)
            for row in rows:
                payload_values.append([str(item) if item is not None else "" for item in row])

            # 3. Clear existing sheet contents and overwrite
            client.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_title}'!A1:Z",
            ).execute()

            # 4. Write new data
            client.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_title}'!A1",
                valueInputOption="USER_ENTERED",
                body={"values": payload_values},
            ).execute()

            logger.info(f"Successfully synced {len(rows)} rows to Google Sheet '{sheet_title}'.")
            return True

        except Exception as exc:
            logger.error(f"Failed to sync data to Google Sheets ({spreadsheet_id}): {exc}", exc_info=True)
            return False


gsheets_exporter = GSheetsExporterService()
