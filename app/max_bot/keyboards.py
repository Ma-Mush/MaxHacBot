"""Keyboard and interactive button builders for MAX Messenger Bot."""
from typing import Any, Dict, List
from app.reports.registry import report_registry


def create_callback_button(text: str, payload: str) -> Dict[str, Any]:
    """Build a single callback button conforming to MAX Bot API."""
    return {
        "type": "callback",
        "text": text,
        "payload": payload,
    }


def create_link_button(text: str, url: str) -> Dict[str, Any]:
    """Build a URL link button conforming to MAX Bot API."""
    return {
        "type": "link",
        "text": text,
        "url": url,
    }


def build_keyboard_attachment(rows: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Wrap rows of buttons into MAX inline_keyboard attachment."""
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": rows,
        },
    }


def get_max_reports_keyboard() -> Dict[str, Any]:
    """Build inline keyboard listing all available report plugins."""
    reports = report_registry.list_reports()
    rows: List[List[Dict[str, Any]]] = []

    for report in reports:
        icon = "📈" if "ecommerce" in report.report_id else "📊"
        title = report.display_name if report.display_name.startswith(("📈", "📊", "🌐")) else f"{icon} {report.display_name}"
        rows.append([create_callback_button(title, f"rep:sel:{report.report_id}")])

    rows.append([create_callback_button("📦 Импортировать с маркетплейса", "rep:menu:marketplaces")])
    rows.append([create_callback_button("🧠 Режим аналитики и AI", "rep:menu:ai")])
    rows.append([create_callback_button("🔄 Обновить список плагинов", "rep:refresh")])
    return build_keyboard_attachment(rows)


def get_max_marketplaces_keyboard() -> Dict[str, Any]:
    """Build inline keyboard with supported marketplaces for data import."""
    rows: List[List[Dict[str, Any]]] = [
        [
            create_callback_button("🟣 Wildberries", "rep:sync:wb"),
            create_callback_button("🔵 Ozon", "rep:sync:ozon"),
        ],
        [
            create_callback_button("🟡 Яндекс.Маркет", "rep:sync:yandex"),
            create_callback_button("🟢 СберМаркет (Купер)", "rep:sync:sbermarket"),
        ],
        [
            create_callback_button("⬅️ Назад к отчетам", "rep:back:reports"),
        ],
    ]
    return build_keyboard_attachment(rows)


def get_max_date_ranges_keyboard(report_id: str) -> Dict[str, Any]:
    """Build inline keyboard with timeframe options for a selected report."""
    rows: List[List[Dict[str, Any]]] = [
        [
            create_callback_button("⚡ Сегодня", f"rep:rng:{report_id}:today"),
            create_callback_button("📆 Вчера", f"rep:rng:{report_id}:yesterday"),
        ],
        [
            create_callback_button("🗓️ Последние 7 дней", f"rep:rng:{report_id}:last_7_days"),
            create_callback_button("📈 Последние 30 дней", f"rep:rng:{report_id}:last_30_days"),
        ],
        [
            create_callback_button("📊 Текущий месяц", f"rep:rng:{report_id}:this_month"),
        ],
        [
            create_callback_button("⬅️ Назад к списку отчетов", "rep:back:reports"),
        ],
    ]
    return build_keyboard_attachment(rows)


def get_max_formats_keyboard(report_id: str, date_range: str) -> Dict[str, Any]:
    """Build inline keyboard for export format selection."""
    rows: List[List[Dict[str, Any]]] = [
        [
            create_callback_button("⚡ Экспресс-сводка (PNG + Текст)", f"rep:gen:{report_id}:{date_range}:png"),
        ],
        [
            create_callback_button("📄 Корпоративный PDF-отчет", f"rep:gen:{report_id}:{date_range}:pdf"),
            create_callback_button("📊 Книга Excel (.xlsx)", f"rep:gen:{report_id}:{date_range}:excel"),
        ],
        [
            create_callback_button("🚀 Всё сразу (All-in-One)", f"rep:gen:{report_id}:{date_range}:all"),
        ],
        [
            create_callback_button("⬅️ Назад к выбору периода", f"rep:sel:{report_id}"),
        ],
    ]
    return build_keyboard_attachment(rows)


def get_max_refresh_keyboard() -> Dict[str, Any]:
    """Simple keyboard to return to main menu after report delivery."""
    return build_keyboard_attachment([
        [create_callback_button("📊 Вернуться в меню отчетов", "rep:back:reports")],
    ])


def get_max_ai_panel_keyboard(current_mode: str, current_provider: str) -> Dict[str, Any]:
    """Build keyboard for AI & Analytics Control Panel with explicit toggle to disable neural AI."""
    rows: List[List[Dict[str, Any]]] = []

    if current_mode == "heuristic":
        rows.append([
            create_callback_button("✅ ⚡ Встроенный анализатор (Нейросеть выключена)", "ai:set:heuristic"),
        ])
        rows.append([
            create_callback_button("🌐 Включить нейросеть через API", "ai:menu:api"),
        ])
        rows.append([
            create_callback_button("💻 Включить локальную нейросеть (Ollama)", "ai:menu:local"),
        ])
    else:
        rows.append([
            create_callback_button("🛑 Отключить нейроаналитику (Встроенный анализатор)", "ai:set:heuristic"),
        ])
        if current_mode == "api":
            rows.append([
                create_callback_button("⚙️ Настроить облачный API (Активен)", "ai:menu:api"),
            ])
            rows.append([
                create_callback_button("💻 Переключить на локальную Ollama", "ai:menu:local"),
            ])
        else:  # local
            rows.append([
                create_callback_button("⚙️ Настроить локальную Ollama (Активна)", "ai:menu:local"),
            ])
            rows.append([
                create_callback_button("🌐 Переключить на облачный API", "ai:menu:api"),
            ])

    rows.append([
        create_callback_button("⬅️ Назад к меню отчетов", "rep:back:reports"),
    ])
    return build_keyboard_attachment(rows)


def get_max_ai_api_keyboard(active_provider: str, has_key: bool) -> Dict[str, Any]:
    """Build keyboard for cloud LLM API provider selection and key input."""
    def p_btn(name: str, prov_id: str) -> Dict[str, Any]:
        prefix = "✅ " if active_provider == prov_id else ""
        return create_callback_button(f"{prefix}{name}", f"ai:set:api:{prov_id}")

    key_action_text = "🔑 Ввести / сменить API-ключ" if has_key else "🔑 Указать API-ключ"

    rows: List[List[Dict[str, Any]]] = [
        [p_btn("🟢 OpenAI (GPT-4o-mini)", "openai"), p_btn("🔵 DeepSeek API", "deepseek")],
        [p_btn("🟠 GigaChat (Сбер)", "gigachat"), p_btn("⚡ Groq (Llama 3.3)", "groq")],
        [p_btn("🟣 Anthropic (Claude)", "anthropic")],
        [create_callback_button(key_action_text, "ai:action:input_key")],
        [create_callback_button("🛑 Отключить нейросеть (Встроенный)", "ai:set:heuristic")],
        [create_callback_button("⬅️ Назад в панель AI", "rep:menu:ai")],
    ]
    return build_keyboard_attachment(rows)


def get_max_ai_local_keyboard(ollama_online: bool, active_model: str) -> Dict[str, Any]:
    """Build keyboard for local Ollama settings."""
    status_icon = "🟢" if ollama_online else "🔴"
    rows: List[List[Dict[str, Any]]] = [
        [create_callback_button(f"✅ Активировать локальную Ollama ({active_model})", "ai:set:local:activate")],
        [create_callback_button(f"🔄 Проверить статус {status_icon}", "ai:action:check_ollama")],
        [create_callback_button("✏️ Сменить модель Ollama", "ai:action:input_ollama_model")],
        [create_callback_button("🛑 Отключить нейросеть (Встроенный)", "ai:set:heuristic")],
        [create_callback_button("⬅️ Назад в панель AI", "rep:menu:ai")],
    ]
    return build_keyboard_attachment(rows)


def get_max_cancel_keyboard(target: str = "rep:menu:ai") -> Dict[str, Any]:
    """Simple cancel button to abort input state."""
    return build_keyboard_attachment([
        [create_callback_button("❌ Отмена", target)],
    ])
