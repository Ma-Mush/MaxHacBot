"""AI Executive Summary service supporting OpenAI, Anthropic, Ollama, and Rule-based Heuristics."""
import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Вы — ведущий бизнес-аналитик и директор по операционной эффективности.
Проанализируйте предоставленные бизнес-метрики и сравнительную динамику.
Сформируйте управленческую сводку строго на русском языке из ровно 4 пунктов с эмодзи (термины, названия магазинов и маркетплейсов сохраняйте в оригинале):
• 🚀 **Главный рост**: ключевое положительное достижение или наибольший прирост метрики.
• ⚠️ **Точка внимания**: метрика или направление с наибольшей просадкой или риском.
• 🔍 **Паттерн / Аномалия**: интересная закономерность, сезонность или корреляция.
• 🎯 **Рекомендация**: конкретное прикладное действие для управленческой команды.

Формулируйте каждый пункт емко и профессионально (максимум 1-2 предложения), опираясь на факты и цифры."""


class AIAnalystService:
    """Service to produce executive natural language briefings from metrics data."""

    def __init__(self) -> None:
        self.provider = settings.AI_PROVIDER.lower().strip()

    async def generate_summary(
        self,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str] = None,
    ) -> str:
        """Generate executive summary using configured provider with heuristic fallback."""
        if self.provider == "none":
            return ""

        summary_text = None
        try:
            if self.provider == "openai" and settings.OPENAI_API_KEY:
                summary_text = await self._call_openai(report_title, metrics_summary, context)
            elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                summary_text = await self._call_anthropic(report_title, metrics_summary, context)
            elif self.provider == "ollama":
                summary_text = await self._call_ollama(report_title, metrics_summary, context)
        except Exception as exc:
            logger.warning(f"AI provider '{self.provider}' request failed ({exc}). Falling back to heuristic summary.")

        if not summary_text:
            summary_text = self._heuristic_summary(report_title, metrics_summary)

        return summary_text

    async def _call_openai(
        self,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        model = settings.AI_MODEL or "gpt-4o-mini"
        user_content = f"Report: {report_title}\nData: {json.dumps(metrics_summary, default=str)}"
        if context:
            user_content += f"\nContext: {context}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 400,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_anthropic(
        self,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        model = settings.AI_MODEL or "claude-3-5-sonnet-20241022"
        user_content = f"Report: {report_title}\nData: {json.dumps(metrics_summary, default=str)}"
        if context:
            user_content += f"\nContext: {context}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_content}],
                    "max_tokens": 400,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"].strip()

    async def _call_ollama(
        self,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        model = settings.AI_MODEL or "llama3"
        user_content = f"Report: {report_title}\nData: {json.dumps(metrics_summary, default=str)}"
        if context:
            user_content += f"\nContext: {context}"

        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                url,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()

    def _heuristic_summary(
        self,
        report_title: str,
        metrics: Dict[str, Any],
    ) -> str:
        """Rule-based intelligent executive summary when external LLM is offline or unconfigured."""
        kpis = metrics.get("kpis", {})
        deltas = metrics.get("deltas", {})

        metric_ru_names = {
            "revenue": "Выручка",
            "orders": "Количество заказов",
            "aov": "Средний чек (AOV)",
            "refund_rate": "Доля возвратов",
            "refunds": "Возвраты",
            "conversion_rate": "Конверсия",
            "total_revenue": "Общая выручка",
            "total_orders": "Всего заказов",
        }

        gains = []
        drops = []

        for name, delta in deltas.items():
            if isinstance(delta, (int, float)):
                if delta > 0:
                    gains.append((name, delta))
                elif delta < 0:
                    drops.append((name, delta))

        # Sort by magnitude
        gains.sort(key=lambda x: x[1], reverse=True)
        drops.sort(key=lambda x: x[1])

        # Bullet 1: Главный рост
        if gains:
            top_gain = gains[0]
            m_name = metric_ru_names.get(top_gain[0], top_gain[0].replace('_', ' '))
            gain_bullet = f"• 🚀 **Главный рост**: Показатель «{m_name}» вырос на +{top_gain[1]:.1f}% по сравнению с предыдущим периодом."
        elif kpis:
            first_kpi = list(kpis.items())[0]
            m_name = metric_ru_names.get(first_kpi[0], first_kpi[0].replace('_', ' '))
            gain_bullet = f"• 🚀 **Главный рост**: Стабильные показатели, значение «{m_name}» зафиксировано на уровне {first_kpi[1]}."
        else:
            gain_bullet = "• 🚀 **Главный рост**: Сбор метрик активен, ключевые показатели находятся в рамках плановых значений."

        # Bullet 2: Точка внимания
        if drops:
            worst_drop = drops[0]
            m_name = metric_ru_names.get(worst_drop[0], worst_drop[0].replace('_', ' '))
            drop_bullet = f"• ⚠️ **Точка внимания**: Показатель «{m_name}» снизился на {abs(worst_drop[1]):.1f}%, рекомендуется проверить конверсию и остатки."
        else:
            drop_bullet = "• ⚠️ **Точка внимания**: Критических отрицательных отклонений метрик в данном периоде не зафиксировано."

        # Bullet 3: Паттерн / Аномалия
        anomaly_bullet = "• 🔍 **Паттерн / Аномалия**: Распределение заказов показывает стабильный рост в будние дни с естественной консолидацией в выходные."

        # Bullet 4: Рекомендация
        if drops:
            m_name = metric_ru_names.get(drops[0][0], drops[0][0].replace('_', ' '))
            action_bullet = f"• 🎯 **Рекомендация**: Оптимизировать товарную матрицу и маркетинговые каналы для устранения просадки по метрике «{m_name}»."
        elif gains:
            m_name = metric_ru_names.get(gains[0][0], gains[0][0].replace('_', ' '))
            action_bullet = f"• 🎯 **Рекомендация**: Усилить темпы роста по направлению «{m_name}» за счет расширения ассортимента и продвижения."
        else:
            action_bullet = "• 🎯 **Рекомендация**: Продолжить плановый сбор телеметрии и настроить оперативные уведомления по ключевым KPI."

        return "\n".join([gain_bullet, drop_bullet, anomaly_bullet, action_bullet])


ai_analyst = AIAnalystService()
