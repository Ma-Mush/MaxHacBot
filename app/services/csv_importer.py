from __future__ import annotations

"""CSV and Excel data ingestion service with intelligent column mapping."""
import csv
from datetime import datetime, timezone
import io
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Column name synonyms for fuzzy matching
DATE_SYNONYMS = ["date", "datetime", "timestamp", "дата", "время", "день", "период", "created_at", "time"]
REVENUE_SYNONYMS = ["revenue", "amount", "total", "price", "sum", "выручка", "сумма", "цена", "продажи", "оборот", "доход"]
ORDERS_SYNONYMS = ["количество", "кол-во", "кол", "шт", "quantity", "count", "orders_count", "чеки", "заказы", "заказов", "заказ", "orders"]
REFUNDS_SYNONYMS = ["refund", "refunds", "возврат", "возвраты"]
VISITORS_SYNONYMS = ["visitors", "visits", "трафик", "посетители", "визиты", "сессии", "sessions", "клики"]
CHANNEL_SYNONYMS = ["channel", "source", "канал", "источник", "utm_source", "тип_трафика"]
REGION_SYNONYMS = ["region", "city", "регион", "город", "страна", "локация"]


class CSVImporterService:
    """Service to parse, normalize, and ingest CSV/Excel spreadsheets into MetricRecord telemetry."""

    @staticmethod
    def _clean_str(val: Any) -> str:
        return str(val or "").strip().lower()

    @staticmethod
    def _parse_num(val: Any) -> Optional[float]:
        """Convert string to clean float, removing spaces and currency signs."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip().replace(" ", "").replace("\xa0", "").replace(",", ".")
        # Remove any currency symbols like ₽, $, €, etc.
        val_str = re.sub(r"[^\d.-]", "", val_str)
        try:
            return float(val_str) if val_str else None
        except ValueError:
            return None

    @staticmethod
    def _parse_datetime(val: Any) -> datetime:
        """Parse various date formats into timezone-aware UTC datetime."""
        if isinstance(val, datetime):
            if val.tzinfo is None:
                return val.replace(tzinfo=timezone.utc)
            return val

        val_str = str(val).strip()
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        # ISO format fallback
        try:
            return datetime.fromisoformat(val_str).replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

    def _detect_columns(self, headers: List[str]) -> Dict[str, str]:
        """Map CSV headers to canonical metric dimensions."""
        mapping: Dict[str, str] = {}
        for h in headers:
            clean_h = self._clean_str(h)
            if any(s in clean_h for s in DATE_SYNONYMS) and "date" not in mapping:
                mapping["date"] = h
            elif any(s in clean_h for s in REVENUE_SYNONYMS) and "revenue" not in mapping:
                mapping["revenue"] = h
            elif (
                any(s in clean_h for s in ORDERS_SYNONYMS)
                and not any(x in clean_h for x in ("номер", "id", "код", "number", "num", "№"))
                and "orders" not in mapping
            ):
                mapping["orders"] = h
            elif any(s in clean_h for s in REFUNDS_SYNONYMS) and "refunds" not in mapping:
                mapping["refunds"] = h
            elif any(s in clean_h for s in VISITORS_SYNONYMS) and "visitors" not in mapping:
                mapping["visitors"] = h
            elif any(s in clean_h for s in CHANNEL_SYNONYMS) and "channel" not in mapping:
                mapping["channel"] = h
            elif any(s in clean_h for s in REGION_SYNONYMS) and "region" not in mapping:
                mapping["region"] = h
        return mapping

    def parse_csv_rows(self, content_str: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Parse raw CSV string with auto-detected delimiter."""
        # Detect delimiter
        first_line = content_str.split("\n", 1)[0]
        delimiter = ";" if ";" in first_line else ("\t" if "\t" in first_line else ",")

        reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
        headers = reader.fieldnames or []
        rows = [row for row in reader if row]
        return list(headers), rows

    def parse_excel_rows(self, file_bytes: bytes) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Parse Excel workbook bytes (.xlsx) using openpyxl."""
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        sheet = wb.active
        if not sheet:
            return [], []

        raw_rows = list(sheet.iter_rows(values_only=True))
        if not raw_rows:
            return [], []

        headers = [str(c or "").strip() for c in raw_rows[0]]
        rows = []
        for r in raw_rows[1:]:
            if any(c is not None for c in r):
                row_dict = {headers[i]: r[i] for i in range(min(len(headers), len(r)))}
                rows.append(row_dict)

        return headers, rows

    async def import_data(
        self,
        file_bytes: bytes,
        filename: str,
        session: Optional[AsyncSession] = None,
        default_unit: str = "RUB",
    ) -> Dict[str, Any]:
        """Parse and ingest file into database, returning structured summary."""
        is_excel = filename.lower().endswith((".xlsx", ".xls"))
        if is_excel:
            headers, rows = self.parse_excel_rows(file_bytes)
        else:
            try:
                content_str = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content_str = file_bytes.decode("cp1251", errors="replace")
            headers, rows = self.parse_csv_rows(content_str)

        if not rows:
            return {"success": False, "error": "No valid data rows found in file."}

        col_map = self._detect_columns(headers)
        logger.info(f"CSV Ingestion mapping for '{filename}': {col_map}")

        date_col = col_map.get("date")
        rev_col = col_map.get("revenue")
        ord_col = col_map.get("orders")
        ref_col = col_map.get("refunds")
        vis_col = col_map.get("visitors")
        chan_col = col_map.get("channel")
        reg_col = col_map.get("region")

        from app.models.metric import MetricRecord
        from app.core.database import async_session_maker

        records: List[Any] = []
        total_rev = 0.0
        total_orders = 0
        min_dt: Optional[datetime] = None
        max_dt: Optional[datetime] = None
        channels_seen = set()

        for row in rows:
            # Timestamp
            ts = self._parse_datetime(row[date_col]) if date_col and date_col in row else datetime.now(timezone.utc)
            if min_dt is None or ts < min_dt:
                min_dt = ts
            if max_dt is None or ts > max_dt:
                max_dt = ts

            # Dimensional tags
            tags: Dict[str, str] = {}
            if chan_col and row.get(chan_col):
                ch_val = str(row[chan_col]).strip()
                tags["channel"] = ch_val
                channels_seen.add(ch_val)
            if reg_col and row.get(reg_col):
                tags["region"] = str(row[reg_col]).strip()

            # Include any other categorical columns as tags
            for h in headers:
                if h not in (date_col, rev_col, ord_col, ref_col, vis_col):
                    val = row.get(h)
                    if val is not None and str(val).strip():
                        tags[self._clean_str(h)] = str(val).strip()

            # 1. Revenue
            if rev_col and row.get(rev_col) is not None:
                rev_val = self._parse_num(row[rev_col])
                if rev_val is not None:
                    records.append(
                        MetricRecord(
                            name="revenue",
                            value=rev_val,
                            unit=default_unit,
                            timestamp=ts,
                            tags=tags,
                        )
                    )
                    total_rev += rev_val

            # 2. Orders count
            if ord_col and row.get(ord_col) is not None:
                ord_val = self._parse_num(row[ord_col])
                if ord_val is not None:
                    records.append(
                        MetricRecord(
                            name="orders_count",
                            value=ord_val,
                            unit="pcs",
                            timestamp=ts,
                            tags=tags,
                        )
                    )
                    total_orders += int(ord_val)

            # 3. Refunds
            if ref_col and row.get(ref_col) is not None:
                ref_val = self._parse_num(row[ref_col])
                if ref_val is not None:
                    records.append(
                        MetricRecord(
                            name="refunds",
                            value=ref_val,
                            unit=default_unit,
                            timestamp=ts,
                            tags=tags,
                        )
                    )

            # 4. Visitors
            if vis_col and row.get(vis_col) is not None:
                vis_val = self._parse_num(row[vis_col])
                if vis_val is not None:
                    records.append(
                        MetricRecord(
                            name="visitors",
                            value=vis_val,
                            unit="users",
                            timestamp=ts,
                            tags=tags,
                        )
                    )

            # Fallback: if row has explicit 'name' and 'value' fields
            if not rev_col and "name" in row and "value" in row:
                m_name = str(row["name"]).strip().lower()
                m_val = self._parse_num(row["value"])
                if m_val is not None:
                    records.append(
                        MetricRecord(
                            name=m_name,
                            value=m_val,
                            unit=str(row.get("unit", "units")),
                            timestamp=ts,
                            tags=tags,
                        )
                    )

        if not records:
            return {
                "success": False,
                "error": "Could not identify any numerical metrics. Verify column headers contain revenue, orders, or date.",
            }

        # Save to database in chunks
        chunk_size = 500
        if session:
            for i in range(0, len(records), chunk_size):
                session.add_all(records[i : i + chunk_size])
            await session.commit()
        else:
            async with async_session_maker() as new_session:
                for i in range(0, len(records), chunk_size):
                    new_session.add_all(records[i : i + chunk_size])
                await new_session.commit()

        return {
            "success": True,
            "filename": filename,
            "total_rows": len(rows),
            "metrics_created": len(records),
            "date_from": min_dt.strftime("%Y-%m-%d") if min_dt else "N/A",
            "date_to": max_dt.strftime("%Y-%m-%d") if max_dt else "N/A",
            "total_revenue": round(total_rev, 2),
            "total_orders": total_orders,
            "channels": list(channels_seen),
            "columns_detected": col_map,
        }


csv_importer = CSVImporterService()
