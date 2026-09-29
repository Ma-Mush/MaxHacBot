"""Tests for AI Analyst service dynamic switching and fallback mechanisms."""
import pytest
from app.services.ai_analyst import AIAnalystService


@pytest.mark.asyncio
async def test_ai_analyst_heuristic_mode():
    """Verify heuristic rule-based analyst produces 4 formatted Russian points."""
    service = AIAnalystService()
    service.set_mode("heuristic")

    metrics_summary = {
        "revenue": 150000.0,
        "revenue_delta": 18.5,
        "orders": 120,
        "orders_delta": 5.2,
        "aov": 1250.0,
        "refunds": 3200.0,
        "refunds_delta": -12.0,
        "channels": {"direct": 80000, "organic": 45000, "ads": 25000},
    }

    summary = await service.generate_summary("Ecommerce Summary", metrics_summary)

    assert "Главный рост" in summary
    assert "Точка внимания" in summary
    assert "Паттерн / Аномалия" in summary
    assert "Рекомендация" in summary
    assert "•" in summary


@pytest.mark.asyncio
async def test_ai_analyst_api_mode_fallback_without_key():
    """Verify API mode without key gracefully falls back to heuristic with a disclaimer."""
    service = AIAnalystService()
    service.set_mode("api")
    service.set_api_provider("openai")
    service.set_api_key("openai", "")  # Empty key

    metrics_summary = {
        "revenue": 50000.0,
        "revenue_delta": -10.0,
        "orders": 40,
    }

    summary = await service.generate_summary("Sales Report", metrics_summary)

    # Should contain notice about missing key and fall back to heuristic
    assert "не указан" in summary or "резервный" in summary
    assert "Главный рост" in summary or "Точка внимания" in summary


@pytest.mark.asyncio
async def test_ai_analyst_local_mode_offline_fallback():
    """Verify local Ollama mode gracefully falls back when Ollama daemon is offline."""
    service = AIAnalystService()
    service.set_local_model("llama3", base_url="http://127.0.0.1:59999")  # Non-existent port

    metrics_summary = {
        "revenue": 75000.0,
        "orders": 55,
    }

    summary = await service.generate_summary("Local Test", metrics_summary)

    # Should contain fallback notice and valid heuristic output
    assert "Ollama" in summary or "недоступна" in summary or "Главный рост" in summary
    assert "Точка внимания" in summary or "Рекомендация" in summary


def test_ai_analyst_status():
    """Verify get_status returns expected keys and values."""
    service = AIAnalystService()
    service.set_mode("heuristic")
    st = service.get_status()

    assert st["mode"] == "heuristic"
    assert "Встроенный анализатор" in st["mode_title"]
    assert "ollama_url" in st
    assert "api_provider" in st
    assert st["is_ai_enabled"] is False


def test_ai_analyst_disable_ai():
    """Verify disable_ai switches mode back to heuristic and updates titles."""
    service = AIAnalystService()
    service.set_mode("api")
    assert service.is_ai_enabled() is True
    assert "нейросети" in service.get_summary_title()

    service.disable_ai()
    assert service.is_ai_enabled() is False
    assert service.mode == "heuristic"
    assert "Встроенный анализатор" in service.get_status()["mode_title"]
    assert "встроенного анализатора" in service.get_summary_title()

