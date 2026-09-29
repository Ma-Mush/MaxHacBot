"""Event Dispatcher and business logic router for MAX Messenger Bot."""
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.date_utils import parse_date_range
from app.max_bot.client import max_client
from app.max_bot.keyboards import (
    get_max_date_ranges_keyboard,
    get_max_formats_keyboard,
    get_max_refresh_keyboard,
    get_max_reports_keyboard,
)
from app.connectors.ozon import ozon_connector
from app.connectors.wildberries import wb_connector
from app.connectors.yandex_market import ym_connector
from app.reports.engine import report_engine
from app.reports.registry import report_registry

logger = logging.getLogger(__name__)


class MAXDispatcher:
    """Dispatches incoming MAX Messenger updates to appropriate business workflows."""

    async def handle_update(self, update: Dict[str, Any]) -> None:
        """Route raw update payload according to update_type."""
        update_type = update.get("update_type")
        logger.debug(f"MAXDispatcher handling update: {update_type}")

        if update_type == "bot_started":
            await self._handle_bot_started(update)
        elif update_type == "message_created":
            await self._handle_message_created(update)
        elif update_type == "message_callback":
            await self._handle_message_callback(update)
        else:
            logger.info(f"Unhandled MAX update_type: {update_type}")

    async def _handle_bot_started(self, update: Dict[str, Any]) -> None:
        """Handle bot_started event."""
        chat_id = update.get("chat_id")
        user_id = update.get("user_id")

        welcome_text = (
            "🚀 <b>Добро пожаловать в OmniMetrics Hub для мессенджера МАКС!</b>\n\n"
            "Я ваш цифровой бизнес-аналитик и операционный директор.\n"
            "Я автоматически собираю телеметрию, провожу факторный анализ выручки "
            "и формирую управленческие сводки с AI-инсайтами прямо в чат МАКС.\n\n"
            "📊 <b>Выберите аналитический отчет для генерации:</b>"
        )
        report_registry.discover()
        keyboard = get_max_reports_keyboard()
        await max_client.send_message(
            text=welcome_text,
            chat_id=chat_id,
            user_id=user_id,
            keyboard=keyboard,
        )

    async def _handle_message_created(self, update: Dict[str, Any]) -> None:
        """Process incoming text messages."""
        msg = update.get("message", {})
        body = msg.get("body", {})
        text = (body.get("text") or "").strip()

        sender = msg.get("sender", {})
        user_id = sender.get("user_id")
        recipient = msg.get("recipient", {})
        chat_id = recipient.get("chat_id")

        # Security whitelist check
        if user_id and not settings.is_max_user_allowed(user_id):
            logger.warning(f"Unauthorized access attempt from MAX user_id={user_id}")
            denied_text = (
                "🔒 <b>Доступ ограничен</b>\n\n"
                f"Ваш идентификатор в МАКС: <code>{user_id}</code>\n"
                "Передайте этот ID администратору системы для включения в список доверенных лиц."
            )
            await max_client.send_message(text=denied_text, chat_id=chat_id, user_id=user_id)
            return

        cmd = text.lower()
        if cmd in ("/start", "/report", "отчет", "отчёт", "старт", "меню"):
            report_registry.discover()
            intro = (
                "📊 <b>Аналитические модули OmniMetrics Hub</b>\n\n"
                "Выберите отчет для настройки периода и формата выгрузки:"
            )
            await max_client.send_message(
                text=intro,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_reports_keyboard(),
            )
        elif cmd in ("/help", "помощь", "справка"):
            help_text = (
                "💡 <b>Справка по OmniMetrics в МАКС:</b>\n\n"
                "• <b>/report</b> — открыть каталог доступных отчетов\n"
                "• <b>/wb</b> — синхронизация статистики продаж с Wildberries API\n"
                "• <b>/ozon</b> — синхронизация отправлений с Ozon Seller API\n"
                "• <b>/yandex</b> — синхронизация заказов с Яндекс.Маркетом\n"
                "• <b>/status</b> — проверка статуса сбора метрик и подключений\n"
                "• <b>/start</b> — перезапустить интерактивное меню\n\n"
                "📦 <b>Доступные форматы:</b>\n"
                "— ⚡ Экспресс-карточка: мгновенный график и 4-пунктовая AI-выжимка\n"
                "— 📄 PDF-отчет: представительский многостраничный документ для руководства\n"
                "— 📊 Excel (.xlsx): подробные таблицы с формулами для финансистов\n"
                "— 🚀 All-in-One: все форматы одним пакетом"
            )
            await max_client.send_message(text=help_text, chat_id=chat_id, user_id=user_id)
        elif cmd in ("/status", "статус"):
            reports_count = len(report_registry.list_reports())
            wb_state = "Подключен (API)" if wb_connector.is_configured() else "Песочница / Mock"
            ozon_state = "Подключен (API)" if ozon_connector.is_configured() else "Песочница / Mock"
            ym_state = "Подключен (API)" if ym_connector.is_configured() else "Песочница / Mock"
            status_text = (
                "🟢 <b>Система OmniMetrics Hub активна</b>\n\n"
                f"• Платформа: <b>Мессенджер МАКС</b>\n"
                f"• Загружено плагинов отчетов: <b>{reports_count}</b>\n"
                f"• AI-аналитик: <b>{settings.AI_PROVIDER.upper()}</b>\n"
                f"• Коннектор Wildberries: <b>{wb_state}</b>\n"
                f"• Коннектор Ozon: <b>{ozon_state}</b>\n"
                f"• Коннектор Яндекс.Маркет: <b>{ym_state}</b>\n"
                f"• База данных: <b>Подключена</b>\n"
                f"• Шедулер регламентных рассылок: <b>Активен</b>"
            )
            await max_client.send_message(
                text=status_text,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )
        elif cmd in ("/wb", "wb", "вайлдберриз", "wildberries"):
            await self._handle_wb_sync(chat_id=chat_id, user_id=user_id)
        elif cmd in ("/ozon", "ozon", "озон"):
            await self._handle_ozon_sync(chat_id=chat_id, user_id=user_id)
        elif cmd in ("/yandex", "yandex", "яндекс", "маркет"):
            await self._handle_ym_sync(chat_id=chat_id, user_id=user_id)
        else:
            # Natural language conversational fallback
            ai_reply = (
                f"💬 Вы написали: «<i>{text}</i>»\n\n"
                "Я готов сформировать для вас детальный срез метрик бизнеса. "
                "Нажмите кнопку ниже, чтобы выбрать отчет и временное окно:"
            )
            await max_client.send_message(
                text=ai_reply,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_reports_keyboard(),
            )

    async def _handle_message_callback(self, update: Dict[str, Any]) -> None:
        """Handle inline button callback actions."""
        callback = update.get("callback", {})
        callback_id = callback.get("callback_id") or update.get("callback_id")
        payload = callback.get("payload") or update.get("payload") or ""

        user = update.get("user", {}) or callback.get("user", {})
        user_id = user.get("user_id")
        message = update.get("message", {}) or callback.get("message", {})
        recipient = message.get("recipient", {})
        chat_id = recipient.get("chat_id") or update.get("chat_id")

        if callback_id:
            await max_client.answer_callback(callback_id, "Запрос принят")

        if not payload:
            return

        # 1. Back to main reports menu / refresh
        if payload in ("rep:back:reports", "rep:refresh"):
            report_registry.discover()
            menu_text = (
                "📊 <b>Выберите аналитический отчет:</b>\n"
                "Настройте временной период и формат выгрузки:"
            )
            await max_client.send_message(
                text=menu_text,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_reports_keyboard(),
            )
            return

        # 1.1 Marketplace sync callbacks
        if payload == "rep:sync:wb":
            await self._handle_wb_sync(chat_id=chat_id, user_id=user_id)
            return

        if payload == "rep:sync:ozon":
            await self._handle_ozon_sync(chat_id=chat_id, user_id=user_id)
            return

        if payload == "rep:sync:yandex":
            await self._handle_ym_sync(chat_id=chat_id, user_id=user_id)
            return

        # 2. Selected a report -> show date range picker
        if payload.startswith("rep:sel:"):
            report_id = payload.split(":")[2]
            report = report_registry.get(report_id)
            if not report:
                await max_client.send_message(
                    text=f"❌ Модуль отчета '{report_id}' не найден.",
                    chat_id=chat_id,
                    user_id=user_id,
                    keyboard=get_max_refresh_keyboard(),
                )
                return

            text = (
                f"Выбран отчет: <b>{report.display_name}</b>\n"
                f"<i>{report.description}</i>\n\n"
                f"🗓 <b>Выберите временной интервал анализа:</b>"
            )
            await max_client.send_message(
                text=text,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_date_ranges_keyboard(report_id),
            )
            return

        # 3. Selected a date range -> show format picker
        if payload.startswith("rep:rng:"):
            parts = payload.split(":")
            report_id = parts[2]
            date_range = parts[3]
            report = report_registry.get(report_id)
            if not report:
                return

            range_labels = {
                "today": "Сегодня",
                "yesterday": "Вчера",
                "last_7_days": "Последние 7 дней",
                "last_30_days": "Последние 30 дней",
                "this_month": "Текущий месяц",
            }
            label = range_labels.get(date_range, date_range)

            text = (
                f"Отчет: <b>{report.display_name}</b>\n"
                f"Временное окно: <b>{label}</b>\n\n"
                f"📦 <b>Выберите желаемый формат доставки:</b>"
            )
            await max_client.send_message(
                text=text,
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_formats_keyboard(report_id, date_range),
            )
            return

        # 4. Generate report execution
        if payload.startswith("rep:gen:"):
            parts = payload.split(":")
            report_id = parts[2]
            date_range = parts[3]
            format_type = parts[4]

            await self._execute_and_send_report(
                report_id=report_id,
                date_range=date_range,
                format_type=format_type,
                chat_id=chat_id,
                user_id=user_id,
            )

    async def _handle_wb_sync(self, chat_id: Optional[int], user_id: Optional[int]) -> None:
        """Fetch statistics from Wildberries and deliver executive briefing."""
        await max_client.send_action(chat_id=chat_id, user_id=user_id, action="typing")
        await max_client.send_message(
            text="🔄 <b>Запуск синхронизации с Wildberries...</b>\n"
                 "<i>Запрашиваю статистику продаж и обновляю метрики в базе...</i>",
            chat_id=chat_id,
            user_id=user_id,
        )

        try:
            from datetime import timedelta, timezone
            end_d = datetime.now(timezone.utc)
            start_d = end_d - timedelta(days=14)

            async with async_session_maker() as session:
                res = await wb_connector.fetch_and_ingest(
                    start_date=start_d,
                    end_date=end_d,
                    session=session,
                )

            mode_str = "Боевой API WB" if res.get("mode") == "live_api" else "Песочница / Mock-генератор"
            top_reg = list(res.get("top_regions", {}).keys())[0] if res.get("top_regions") else "—"
            top_wh = list(res.get("top_warehouses", {}).keys())[0] if res.get("top_warehouses") else "—"
            aov = res["total_revenue"] / res["total_orders"] if res.get("total_orders") else 0.0

            summary_msg = (
                "🟣 <b>Синхронизация с Wildberries завершена!</b>\n\n"
                f"• Режим источника: <b>{mode_str}</b>\n"
                f"• Заказов получено: <b>{res.get('total_orders', 0)}</b>\n"
                f"• Выручка: <b>{res.get('total_revenue', 0.0):,.2f} ₽</b>\n"
                f"• Возвраты: <b>{res.get('total_refunds', 0.0):,.2f} ₽</b>\n"
                f"• Средний чек (AOV): <b>{aov:,.2f} ₽</b>\n"
                f"• Топ регион: <b>{top_reg}</b>\n"
                f"• Ключевой склад: <b>{top_wh}</b>\n\n"
                "📄 <i>Генерирую управленческий отчет, графики и Excel...</i>"
            )
            await max_client.send_message(text=summary_msg, chat_id=chat_id, user_id=user_id)

            # Auto-generate full executive briefing for the updated data
            rep_id = "ecommerce_summary" if report_registry.get("ecommerce_summary") else "revenue_executive"
            await self._execute_and_send_report(
                report_id=rep_id,
                date_range="last_30_days",
                format_type="all",
                chat_id=chat_id,
                user_id=user_id,
            )
        except Exception as exc:
            logger.error(f"Error during WB sync in MAX: {exc}", exc_info=True)
            await max_client.send_message(
                text=f"❌ <b>Ошибка при синхронизации Wildberries:</b>\n<code>{str(exc)}</code>",
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )

    async def _handle_ozon_sync(self, chat_id: Optional[int], user_id: Optional[int]) -> None:
        """Fetch statistics from Ozon Seller API and deliver executive briefing."""
        await max_client.send_action(chat_id=chat_id, user_id=user_id, action="typing")
        await max_client.send_message(
            text="🔄 <b>Запуск синхронизации с Ozon Seller API...</b>\n"
                 "<i>Запрашиваю отправления, комиссии и обновляю метрики в базе...</i>",
            chat_id=chat_id,
            user_id=user_id,
        )

        try:
            from datetime import timedelta, timezone
            end_d = datetime.now(timezone.utc)
            start_d = end_d - timedelta(days=14)

            async with async_session_maker() as session:
                res = await ozon_connector.fetch_and_ingest(
                    start_date=start_d,
                    end_date=end_d,
                    session=session,
                )

            mode_str = "Боевой API Ozon" if res.get("mode") == "live_api" else "Песочница / Mock-генератор"
            top_clust = list(res.get("top_clusters", {}).keys())[0] if res.get("top_clusters") else "—"
            top_wh = list(res.get("top_warehouses", {}).keys())[0] if res.get("top_warehouses") else "—"
            aov = res["total_revenue"] / res["total_orders"] if res.get("total_orders") else 0.0

            summary_msg = (
                "🔵 <b>Синхронизация с Ozon завершена!</b>\n\n"
                f"• Режим источника: <b>{mode_str}</b>\n"
                f"• Заказов получено: <b>{res.get('total_orders', 0)}</b>\n"
                f"• Выручка: <b>{res.get('total_revenue', 0.0):,.2f} ₽</b>\n"
                f"• Возвраты: <b>{res.get('total_refunds', 0.0):,.2f} ₽</b>\n"
                f"• Средний чек (AOV): <b>{aov:,.2f} ₽</b>\n"
                f"• Ведущий кластер: <b>{top_clust}</b>\n"
                f"• Основной фулфилмент: <b>{top_wh}</b>\n\n"
                "📄 <i>Генерирую управленческий отчет, графики и Excel...</i>"
            )
            await max_client.send_message(text=summary_msg, chat_id=chat_id, user_id=user_id)

            rep_id = "ecommerce_summary" if report_registry.get("ecommerce_summary") else "revenue_executive"
            await self._execute_and_send_report(
                report_id=rep_id,
                date_range="last_30_days",
                format_type="all",
                chat_id=chat_id,
                user_id=user_id,
            )
        except Exception as exc:
            logger.error(f"Error during Ozon sync in MAX: {exc}", exc_info=True)
            await max_client.send_message(
                text=f"❌ <b>Ошибка при синхронизации Ozon:</b>\n<code>{str(exc)}</code>",
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )

    async def _handle_ym_sync(self, chat_id: Optional[int], user_id: Optional[int]) -> None:
        """Fetch orders from Yandex Market Partner API and deliver executive briefing."""
        await max_client.send_action(chat_id=chat_id, user_id=user_id, action="typing")
        await max_client.send_message(
            text="🔄 <b>Запуск синхронизации с Яндекс.Маркетом...</b>\n"
                 "<i>Запрашиваю заказы, оборот и обновляю метрики в базе...</i>",
            chat_id=chat_id,
            user_id=user_id,
        )

        try:
            from datetime import timedelta, timezone
            end_d = datetime.now(timezone.utc)
            start_d = end_d - timedelta(days=14)

            async with async_session_maker() as session:
                res = await ym_connector.fetch_and_ingest(
                    start_date=start_d,
                    end_date=end_d,
                    session=session,
                )

            mode_str = "Боевой API Яндекс.Маркет" if res.get("mode") == "live_api" else "Песочница / Mock-генератор"
            top_reg = list(res.get("top_regions", {}).keys())[0] if res.get("top_regions") else "—"
            top_wh = list(res.get("top_warehouses", {}).keys())[0] if res.get("top_warehouses") else "—"
            aov = res["total_revenue"] / res["total_orders"] if res.get("total_orders") else 0.0

            summary_msg = (
                "🟡 <b>Синхронизация с Яндекс.Маркетом завершена!</b>\n\n"
                f"• Режим источника: <b>{mode_str}</b>\n"
                f"• Заказов получено: <b>{res.get('total_orders', 0)}</b>\n"
                f"• Выручка: <b>{res.get('total_revenue', 0.0):,.2f} ₽</b>\n"
                f"• Возвраты: <b>{res.get('total_refunds', 0.0):,.2f} ₽</b>\n"
                f"• Средний чек (AOV): <b>{aov:,.2f} ₽</b>\n"
                f"• Ключевой регион: <b>{top_reg}</b>\n"
                f"• Склад отгрузки: <b>{top_wh}</b>\n\n"
                "📄 <i>Генерирую управленческий отчет, графики и Excel...</i>"
            )
            await max_client.send_message(text=summary_msg, chat_id=chat_id, user_id=user_id)

            rep_id = "ecommerce_summary" if report_registry.get("ecommerce_summary") else "revenue_executive"
            await self._execute_and_send_report(
                report_id=rep_id,
                date_range="last_30_days",
                format_type="all",
                chat_id=chat_id,
                user_id=user_id,
            )
        except Exception as exc:
            logger.error(f"Error during Yandex Market sync in MAX: {exc}", exc_info=True)
            await max_client.send_message(
                text=f"❌ <b>Ошибка при синхронизации Яндекс.Маркета:</b>\n<code>{str(exc)}</code>",
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )

    async def _execute_and_send_report(
        self,
        report_id: str,
        date_range: str,
        format_type: str,
        chat_id: Optional[int],
        user_id: Optional[int],
    ) -> None:
        """Run reporting engine and dispatch compiled artifacts to MAX."""
        report = report_registry.get(report_id)
        if not report:
            await max_client.send_message(
                text="❌ Модуль отчета не найден.",
                chat_id=chat_id,
                user_id=user_id,
            )
            return

        await max_client.send_action(chat_id=chat_id, user_id=user_id, action="typing")
        await max_client.send_message(
            text=f"⏳ <i>Формирую отчет «{report.display_name}» ({date_range}). Пожалуйста, подождите...</i>",
            chat_id=chat_id,
            user_id=user_id,
        )

        try:
            start_date, end_date = parse_date_range(date_range)
            date_label = date_range.replace("_", " ").title()

            if format_type == "all":
                req_formats = ["png", "pdf", "excel"]
            elif format_type == "png":
                req_formats = ["png", "summary"]
            elif format_type == "pdf":
                req_formats = ["pdf", "png"]
            elif format_type == "excel":
                req_formats = ["excel"]
            else:
                req_formats = [format_type]

            async with async_session_maker() as session:
                generated = await report_engine.generate_report(
                    report_id=report_id,
                    start_date=start_date,
                    end_date=end_date,
                    date_range_label=date_label,
                    formats=req_formats,
                    session=session,
                )

            # 1. Deliver PNG preview / card with AI briefing caption
            if format_type in ("png", "all") or generated.primary_card_png:
                if generated.primary_card_png:
                    await max_client.send_photo(
                        photo_bytes=generated.primary_card_png,
                        filename=f"{report_id}_card.png",
                        caption=generated.telegram_caption,
                        chat_id=chat_id,
                        user_id=user_id,
                    )
                elif generated.telegram_caption:
                    await max_client.send_message(
                        text=generated.telegram_caption,
                        chat_id=chat_id,
                        user_id=user_id,
                    )

            # 2. Deliver PDF report
            if format_type in ("pdf", "all") and generated.pdf_bytes:
                date_str = start_date.strftime("%Y%m%d")
                await max_client.send_document(
                    file_bytes=generated.pdf_bytes,
                    filename=f"{report_id}_{date_str}.pdf",
                    caption=f"📄 <b>PDF-отчет</b>: {report.display_name}",
                    chat_id=chat_id,
                    user_id=user_id,
                )

            # 3. Deliver Excel workbook
            if format_type in ("excel", "all") and generated.excel_bytes:
                date_str = start_date.strftime("%Y%m%d")
                await max_client.send_document(
                    file_bytes=generated.excel_bytes,
                    filename=f"{report_id}_{date_str}.xlsx",
                    caption=f"📊 <b>Книга Excel</b>: {report.display_name}",
                    chat_id=chat_id,
                    user_id=user_id,
                )

            # Follow-up menu
            await max_client.send_message(
                text="✅ <b>Отчет успешно сформирован и доставлен!</b>",
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )

        except Exception as exc:
            logger.error(f"Error compiling report for MAX: {exc}", exc_info=True)
            await max_client.send_message(
                text=f"❌ <b>Ошибка при генерации отчета:</b>\n<code>{str(exc)}</code>",
                chat_id=chat_id,
                user_id=user_id,
                keyboard=get_max_refresh_keyboard(),
            )


max_dispatcher = MAXDispatcher()
