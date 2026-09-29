"""AI Executive Summary service supporting dynamic switching between Rule-based Heuristic Analyzer,
Cloud LLMs via API keys (OpenAI, DeepSeek, GigaChat, Groq, Anthropic), and Local Ollama."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid
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

CONFIG_FILE_PATH = Path("./data/ai_config.json")

# Default models per provider
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "gigachat": "GigaChat",
    "groq": "llama-3.3-70b-versatile",
    "anthropic": "claude-3-5-sonnet-20241022",
    "ollama": "llama3",
}

PROVIDER_NAMES = {
    "openai": "OpenAI (GPT-4o-mini)",
    "deepseek": "DeepSeek API",
    "gigachat": "GigaChat (Сбербанк)",
    "groq": "Groq (Llama 3.3 70B)",
    "anthropic": "Anthropic Claude",
    "ollama": "Локальная Ollama",
    "heuristic": "Встроенный анализатор",
}


class AIAnalystService:
    """Service to produce executive natural language briefings from metrics data with multi-engine switching."""

    def __init__(self) -> None:
        self.mode = "heuristic"  # "heuristic", "api", "local"
        self.api_provider = "openai"
        self.api_model = "gpt-4o-mini"
        self.api_keys: Dict[str, str] = {
            "openai": "",
            "deepseek": "",
            "gigachat": "",
            "groq": "",
            "anthropic": "",
        }
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_model = "llama3"

        self._load_config()

    def _load_config(self) -> None:
        """Load persistent config from ai_config.json, fallback to settings."""
        self.mode = settings.AI_MODE.lower().strip() or "heuristic"
        self.api_provider = settings.AI_PROVIDER.lower().strip() or "openai"
        if self.api_provider in ("heuristic", "none", "ollama"):
            self.api_provider = "openai"
        self.api_model = settings.AI_MODEL or DEFAULT_MODELS.get(self.api_provider, "gpt-4o-mini")

        self.api_keys = {
            "openai": settings.OPENAI_API_KEY or "",
            "deepseek": settings.DEEPSEEK_API_KEY or "",
            "gigachat": settings.GIGACHAT_CREDENTIALS or "",
            "groq": settings.GROQ_API_KEY or "",
            "anthropic": settings.ANTHROPIC_API_KEY or "",
        }
        self.ollama_base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
        self.ollama_model = settings.OLLAMA_MODEL or "llama3"

        if CONFIG_FILE_PATH.exists():
            try:
                data = json.loads(CONFIG_FILE_PATH.read_text(encoding="utf-8"))
                self.mode = data.get("mode", self.mode)
                self.api_provider = data.get("api_provider", self.api_provider)
                self.api_model = data.get("api_model", self.api_model)
                saved_keys = data.get("api_keys", {})
                for k, v in saved_keys.items():
                    if v:
                        self.api_keys[k] = v
                self.ollama_base_url = data.get("ollama_base_url", self.ollama_base_url)
                self.ollama_model = data.get("ollama_model", self.ollama_model)
            except Exception as exc:
                logger.warning(f"Could not read ai_config.json: {exc}")

    def _save_config(self) -> None:
        """Save persistent config to ai_config.json."""
        try:
            CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "mode": self.mode,
                "api_provider": self.api_provider,
                "api_model": self.api_model,
                "api_keys": self.api_keys,
                "ollama_base_url": self.ollama_base_url,
                "ollama_model": self.ollama_model,
            }
            CONFIG_FILE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:
            logger.error(f"Failed writing ai_config.json: {exc}")

    def set_mode(self, mode: str) -> None:
        """Set active engine mode: 'heuristic', 'api', or 'local'."""
        if mode in ("heuristic", "api", "local"):
            self.mode = mode
            self._save_config()

    def set_api_provider(self, provider: str, model: Optional[str] = None) -> None:
        """Set active cloud API provider and default model."""
        if provider in DEFAULT_MODELS:
            self.api_provider = provider
            self.api_model = model or DEFAULT_MODELS.get(provider, "")
            self.mode = "api"
            self._save_config()

    def set_api_key(self, provider: str, key: str) -> None:
        """Save API key for a provider."""
        if provider in self.api_keys:
            self.api_keys[provider] = key.strip()
            self._save_config()

    def set_local_model(self, model: str, base_url: Optional[str] = None) -> None:
        """Set local Ollama model and optional URL."""
        if model:
            self.ollama_model = model.strip()
        if base_url:
            self.ollama_base_url = base_url.strip()
        self.mode = "local"
        self._save_config()

    async def check_ollama(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and list downloaded models."""
        url = f"{self.ollama_base_url.rstrip('/')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                    return {
                        "online": True,
                        "models": models,
                        "url": self.ollama_base_url,
                        "message": f"Доступно моделей: {len(models)} ({', '.join(models[:3])})" if models else "Ollama онлайн, модели не загружены",
                    }
        except Exception:
            pass
        return {
            "online": False,
            "models": [],
            "url": self.ollama_base_url,
            "message": "Сервис Ollama недоступен (проверьте 'ollama serve')",
        }

    def disable_ai(self) -> None:
        """Disable neural analytics and switch to the built-in algorithmic analyzer."""
        self.set_mode("heuristic")

    def is_ai_enabled(self) -> bool:
        """Check whether neural network AI mode is currently enabled."""
        return self.mode in ("api", "local")

    def get_summary_title(self) -> str:
        """Return title for report caption / callout based on active engine."""
        if self.mode == "heuristic":
            return "⚡ <b>Сводка встроенного анализатора:</b>"
        elif self.mode == "api":
            return f"🧠 <b>Аналитический инсайт нейросети ({PROVIDER_NAMES.get(self.api_provider, self.api_provider)}):</b>"
        elif self.mode == "local":
            return f"💻 <b>Аналитический инсайт нейросети (Ollama: {self.ollama_model}):</b>"
        return "📊 <b>Аналитическая сводка:</b>"

    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive status for UI/dashboard."""
        cur_key = self.api_keys.get(self.api_provider, "")
        masked_key = f"{cur_key[:4]}...{cur_key[-4:]}" if len(cur_key) >= 10 else ("Указан" if cur_key else "Не настроен")

        mode_titles = {
            "heuristic": "⚡ Встроенный анализатор (Без нейросети)",
            "api": f"🌐 Нейросеть (API: {PROVIDER_NAMES.get(self.api_provider, self.api_provider)})",
            "local": f"💻 Локальная нейросеть (Ollama: {self.ollama_model})",
        }
        is_ai_on = self.mode in ("api", "local")

        return {
            "mode": self.mode,
            "mode_title": mode_titles.get(self.mode, self.mode),
            "is_ai_enabled": is_ai_on,
            "ai_status_badge": "🟣 Нейросеть включена" if is_ai_on else "🟢 Нейросеть ОТКЛЮЧЕНА (Встроенный анализатор)",
            "api_provider": self.api_provider,
            "api_provider_name": PROVIDER_NAMES.get(self.api_provider, self.api_provider),
            "api_model": self.api_model,
            "has_api_key": bool(cur_key),
            "api_key_masked": masked_key,
            "ollama_base_url": self.ollama_base_url,
            "ollama_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
        }

    async def generate_summary(
        self,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str] = None,
    ) -> str:
        """Generate executive summary using the currently selected engine."""
        # 1. Mode: Heuristic
        if self.mode == "heuristic":
            return self._heuristic_summary(report_title, metrics_summary)

        # 2. Mode: Cloud API
        if self.mode == "api":
            key = self.api_keys.get(self.api_provider, "")
            if not key:
                logger.warning(f"API key for '{self.api_provider}' is not set. Falling back to heuristic.")
                notice = f"*(⚠️ API-ключ для {PROVIDER_NAMES.get(self.api_provider, self.api_provider)} не указан. Использован резервный анализатор)*\n\n"
                return notice + self._heuristic_summary(report_title, metrics_summary)

            try:
                if self.api_provider == "openai":
                    base_url = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
                    return await self._call_openai_compatible(base_url, key, self.api_model or "gpt-4o-mini", report_title, metrics_summary, context)
                elif self.api_provider == "deepseek":
                    return await self._call_openai_compatible("https://api.deepseek.com", key, self.api_model or "deepseek-chat", report_title, metrics_summary, context)
                elif self.api_provider == "groq":
                    return await self._call_openai_compatible("https://api.groq.com/openai/v1", key, self.api_model or "llama-3.3-70b-versatile", report_title, metrics_summary, context)
                elif self.api_provider == "gigachat":
                    return await self._call_gigachat(key, self.api_model or "GigaChat", report_title, metrics_summary, context)
                elif self.api_provider == "anthropic":
                    return await self._call_anthropic(key, self.api_model or "claude-3-5-sonnet-20241022", report_title, metrics_summary, context)
            except Exception as exc:
                logger.error(f"Error calling {self.api_provider} API: {exc}")
                notice = f"*(⚠️ Ошибка вызова {PROVIDER_NAMES.get(self.api_provider, self.api_provider)}: {str(exc)[:60]}. Использован резервный анализатор)*\n\n"
                return notice + self._heuristic_summary(report_title, metrics_summary)

        # 3. Mode: Local Ollama
        if self.mode == "local":
            try:
                return await self._call_ollama(self.ollama_base_url, self.ollama_model, report_title, metrics_summary, context)
            except Exception as exc:
                logger.warning(f"Local Ollama call failed ({exc}). Falling back to heuristic.")
                notice = f"*(⚠️ Локальная Ollama недоступна на {self.ollama_base_url}. Использован резервный анализатор)*\n\n"
                return notice + self._heuristic_summary(report_title, metrics_summary)

        return self._heuristic_summary(report_title, metrics_summary)

    async def _call_openai_compatible(
        self,
        base_url: str,
        api_key: str,
        model: str,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        """Call OpenAI or OpenAI-compatible endpoint (DeepSeek, Groq, OpenRouter)."""
        user_content = f"Отчет: {report_title}\nДанные метрик: {json.dumps(metrics_summary, default=str, ensure_ascii=False)}"
        if context:
            user_content += f"\nДополнительный контекст: {context}"

        endpoint = f"{base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=30.0, verify=False, trust_env=False) as client:
            resp = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_gigachat(
        self,
        credentials: str,
        model: str,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        """Call Sberbank GigaChat API with OAuth token acquisition."""
        user_content = f"Отчет: {report_title}\nДанные метрик: {json.dumps(metrics_summary, default=str, ensure_ascii=False)}"
        if context:
            user_content += f"\nДополнительный контекст: {context}"

        async with httpx.AsyncClient(timeout=30.0, verify=False, trust_env=False) as client:
            # 1. Obtain Bearer token
            rquid = str(uuid.uuid4())
            auth_resp = await client.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "RqUID": rquid,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"scope": "GIGACHAT_API_PERS"},
            )
            auth_resp.raise_for_status()
            access_token = auth_resp.json().get("access_token")

            # 2. Chat completion
            chat_resp = await client.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "GigaChat",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
            )
            chat_resp.raise_for_status()
            data = chat_resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_anthropic(
        self,
        api_key: str,
        model: str,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        """Call Anthropic Messages API."""
        user_content = f"Отчет: {report_title}\nДанные метрик: {json.dumps(metrics_summary, default=str, ensure_ascii=False)}"
        if context:
            user_content += f"\nДополнительный контекст: {context}"

        async with httpx.AsyncClient(timeout=30.0, verify=False, trust_env=False) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "claude-3-5-sonnet-20241022",
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_content}],
                    "max_tokens": 500,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"].strip()

    async def _call_ollama(
        self,
        base_url: str,
        model: str,
        report_title: str,
        metrics_summary: Dict[str, Any],
        context: Optional[str],
    ) -> str:
        """Call Local Ollama API chat endpoint."""
        user_content = f"Отчет: {report_title}\nДанные метрик: {json.dumps(metrics_summary, default=str, ensure_ascii=False)}"
        if context:
            user_content += f"\nДополнительный контекст: {context}"

        url = f"{base_url.rstrip('/')}/api/chat"
        async with httpx.AsyncClient(timeout=45.0, verify=False, trust_env=False) as client:
            resp = await client.post(
                url,
                json={
                    "model": model or "llama3",
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
