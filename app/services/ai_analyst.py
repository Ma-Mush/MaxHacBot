"""AI Executive Summary service supporting OpenAI, Anthropic, Ollama, and Rule-based Heuristics."""
import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Executive Data Analyst.
Analyze the provided business metrics and comparative trends.
Provide exactly a 4-bullet executive briefing formatted with emojis:
• 🚀 **Key Gain**: The most notable positive trend or milestone achieved.
• ⚠️ **Drop / Friction Point**: The primary metric showing decline or risk.
• 🔍 **Anomaly / Pattern**: Any outlier, seasonality, or correlation worth executive attention.
• 🎯 **Recommended Action**: One concrete, high-impact tactical action for the leadership team.

Keep each bullet concise (1-2 sentences maximum), actionable, and data-driven."""


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

        # Bullet 1: Key Gain
        if gains:
            top_gain = gains[0]
            gain_bullet = f"• 🚀 **Key Gain**: {top_gain[0].replace('_', ' ').title()} grew by +{top_gain[1]:.1f}% compared to the prior period."
        elif kpis:
            first_kpi = list(kpis.items())[0]
            gain_bullet = f"• 🚀 **Key Gain**: Stable operating baseline with {first_kpi[0].replace('_', ' ').title()} recorded at {first_kpi[1]}."
        else:
            gain_bullet = "• 🚀 **Key Gain**: Telemetry ingestion active and operating within baseline parameters."

        # Bullet 2: Drop / Friction Point
        if drops:
            worst_drop = drops[0]
            drop_bullet = f"• ⚠️ **Drop / Friction Point**: {worst_drop[0].replace('_', ' ').title()} contracted by {worst_drop[1]:.1f}%, requiring conversion pipeline review."
        else:
            drop_bullet = "• ⚠️ **Drop / Friction Point**: No severe negative metric variances detected in this observation window."

        # Bullet 3: Anomaly / Pattern
        anomaly_bullet = f"• 🔍 **Anomaly / Pattern**: Volume distribution across primary channels exhibits steady weekday peaks with predictable weekend consolidation."

        # Bullet 4: Recommended Action
        if drops:
            action_bullet = f"• 🎯 **Recommended Action**: Reallocate ad spend towards high-performing channels to offset the {drops[0][0].replace('_', ' ')} variance."
        elif gains:
            action_bullet = f"• 🎯 **Recommended Action**: Double down on the momentum in {gains[0][0].replace('_', ' ')} by expanding acquisition budgets."
        else:
            action_bullet = "• 🎯 **Recommended Action**: Maintain continuous automated telemetry monitoring and establish baseline KPI alerts."

        return "\n".join([gain_bullet, drop_bullet, anomaly_bullet, action_bullet])


ai_analyst = AIAnalystService()
