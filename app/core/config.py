"""Application configuration settings using Pydantic v2."""
import json
from typing import Any, List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core Application Settings
    APP_NAME: str = "OmniMetrics Hub"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    APP_API_KEY: str = "omni_secret_key_change_me"
    API_V1_STR: str = "/api/v1"

    # Database
    # Default to PostgreSQL, with fallback to SQLite for local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./omni_metrics.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    ALLOWED_TELEGRAM_USERS: Union[List[int], str] = []

    # AI Executive Analyst
    # Options: "openai", "anthropic", "ollama", "heuristic", "none"
    AI_PROVIDER: str = "heuristic"
    AI_MODEL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Google Sheets Integration
    GSHEETS_SERVICE_ACCOUNT_FILE: Optional[str] = "service_account.json"
    GSHEETS_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # Scheduler Settings
    SCHEDULER_ENABLED: bool = True
    CRON_MORNING_REPORT: Optional[str] = "0 9 * * 1-5"  # 9 AM Monday-Friday
    DEFAULT_SCHEDULED_CHAT_ID: Optional[int] = None
    DEFAULT_SCHEDULED_REPORT_ID: str = "ecommerce_summary"

    # PDF & Rendering Engine
    PDF_ENGINE: str = "auto"  # "weasyprint", "playwright", "auto"
    OUTPUT_DIR: str = "./output"

    @field_validator("ALLOWED_TELEGRAM_USERS", mode="before")
    @classmethod
    def parse_allowed_telegram_users(cls, v: Any) -> List[int]:
        if isinstance(v, list):
            return [int(x) for x in v if str(x).strip()]
        if isinstance(v, (int, float)):
            return [int(v)]
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return []
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    return [int(x) for x in parsed]
                except Exception:
                    pass
            # Comma-separated list
            result = []
            for item in v_str.split(","):
                item = item.strip()
                if item:
                    try:
                        result.append(int(item))
                    except ValueError:
                        pass
            return result
        return []

    def is_telegram_user_allowed(self, user_id: int) -> bool:
        """Check if user_id is in ALLOWED_TELEGRAM_USERS. If empty, allows none."""
        if not self.ALLOWED_TELEGRAM_USERS:
            return False
        return user_id in self.ALLOWED_TELEGRAM_USERS


settings = Settings()
