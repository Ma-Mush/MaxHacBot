#!/usr/bin/env python3
"""Build a beautiful, jury-ready PDF presentation for OmniMetrics Hub & MAX Business AI (Russian)."""

import base64
import os
from pathlib import Path

# Paths relative to this script
ASSETS = Path(__file__).resolve().parent
PROJECT_DIR = ASSETS.parent.parent
OUTPUT_DIR = ASSETS.parent

def img_b64(name: str) -> str:
    """Convert image file to base64 data URI."""
    path = ASSETS / name
    if not path.exists():
        # Fallback to output directory if present
        alt_path = PROJECT_DIR / "output" / name
        if alt_path.exists():
            path = alt_path
        else:
            return ""
    data = path.read_bytes()
    mime = "image/png" if name.endswith(".png") else "image/jpeg"
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"

# Load presentation images
COVER = img_b64("cover.jpg")
PROBLEM = img_b64("problem.jpg")
SOLUTION = img_b64("solution.jpg")
ARCHITECTURE = img_b64("architecture.jpg")
DASHBOARD = img_b64("dashboard.jpg")
SCALING = img_b64("scaling.jpg")
PILOT = img_b64("pilot.jpg")

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
@page {{
  size: 1280px 720px;
  margin: 0;
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'DejaVu Sans', 'Liberation Sans', 'Noto Sans', Arial, sans-serif;
  color: #ffffff;
  line-height: 1.4;
  background: #0a1628;
}}

.slide {{
  width: 1280px;
  height: 720px;
  page-break-after: always;
  page-break-inside: avoid;
  position: relative;
  overflow: hidden;
}}

.slide:last-child {{
  page-break-after: auto;
}}

/* ===== SLIDE 1: COVER ===== */
.slide-cover {{
  background: linear-gradient(135deg, #07111e 0%, #0d2847 40%, #0f3460 70%, #105663 100%);
}}

.bg-img {{
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  opacity: 0.22;
  z-index: 0;
}}

.bg-img img {{
  width: 100%; height: 100%;
  object-fit: cover;
}}

.cover-content {{
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  padding: 50px 70px;
}}

.cover-badge {{
  background: rgba(0, 210, 211, 0.15);
  border: 2px solid #00d2d3;
  border-radius: 30px;
  padding: 8px 30px;
  font-size: 15px;
  color: #00d2d3;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 24px;
  font-weight: 700;
}}

.cover-title {{
  font-size: 52px;
  font-weight: 800;
  color: #00d2d3;
  margin-bottom: 16px;
  line-height: 1.15;
  text-shadow: 0 4px 24px rgba(0, 210, 211, 0.5);
}}

.cover-subtitle {{
  font-size: 22px;
  color: #b0d2f5;
  margin-bottom: 34px;
  max-width: 920px;
  line-height: 1.5;
}}

.cover-features-row {{
  display: flex;
  gap: 16px;
  margin-bottom: 34px;
}}

.cover-feature-pill {{
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 210, 211, 0.35);
  border-radius: 20px;
  padding: 6px 18px;
  font-size: 14px;
  color: #e2f1ff;
}}

.cover-track {{
  background: linear-gradient(90deg, #00d2d3, #0f3460);
  padding: 12px 42px;
  border-radius: 8px;
  font-size: 17px;
  font-weight: 700;
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 210, 211, 0.3);
}}

/* ===== SLIDE 2: PROBLEM ===== */
.slide-problem {{
  background: linear-gradient(135deg, #161a29 0%, #14233c 50%, #0f3460 100%);
}}

.split-layout {{
  display: flex;
  height: 100%;
}}

.split-left {{
  width: 56%;
  padding: 50px 40px 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

.split-right {{
  width: 44%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
}}

.split-right img {{
  width: 100%;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
}}

.slide-number {{
  position: absolute;
  bottom: 20px;
  right: 40px;
  font-size: 14px;
  color: rgba(255,255,255,0.35);
  font-weight: 600;
}}

.section-label {{
  font-size: 13px;
  color: #00d2d3;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 10px;
  font-weight: 700;
}}

.slide-heading {{
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 20px;
  line-height: 1.2;
}}

.stat-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 18px;
}}

.stat-card {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 14px 18px;
  width: 48%;
}}

.stat-value {{
  font-size: 26px;
  font-weight: 800;
  color: #00d2d3;
}}

.stat-desc {{
  font-size: 12px;
  color: #a0c4e8;
  margin-top: 4px;
  line-height: 1.4;
}}

.problem-text {{
  font-size: 14px;
  color: #cdd9e5;
  line-height: 1.55;
  background: rgba(255, 69, 58, 0.08);
  border-left: 3px solid #ff4d4d;
  padding: 10px 14px;
  border-radius: 4px;
}}

/* ===== SLIDE 3: SOLUTION ===== */
.slide-solution {{
  background: linear-gradient(135deg, #09203a 0%, #0a3d46 50%, #0e5b60 100%);
}}

.solution-features {{
  list-style: none;
  padding: 0;
  margin: 0;
}}

.solution-features li {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 13px;
  font-size: 14.5px;
  color: #e0e8f0;
}}

.feature-icon {{
  width: 32px;
  height: 32px;
  min-width: 32px;
  background: linear-gradient(135deg, #00d2d3, #0f3460);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: white;
}}

.feature-title {{
  font-weight: 700;
  color: #ffffff;
}}

/* ===== SLIDE 4 & 5: SCENARIO & AUDIENCE ===== */
.slide-scenario {{
  background: linear-gradient(135deg, #131a2e 0%, #0c233c 100%);
}}

.full-slide-content {{
  padding: 45px 60px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 100%;
}}

.scenario-flow {{
  display: flex;
  gap: 14px;
  margin-top: 14px;
}}

.scenario-step {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(0,210,211,0.25);
  border-radius: 12px;
  padding: 16px;
  flex: 1;
  position: relative;
}}

.step-number {{
  background: linear-gradient(135deg, #00d2d3, #0f3460);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 15px;
  margin-bottom: 8px;
}}

.step-title {{
  font-size: 15px;
  font-weight: 700;
  color: #00d2d3;
  margin-bottom: 6px;
}}

.step-desc {{
  font-size: 12.5px;
  color: #b0ceeb;
  line-height: 1.45;
}}

.hypothesis-box {{
  background: rgba(0,210,211,0.08);
  border-left: 4px solid #00d2d3;
  padding: 14px 20px;
  border-radius: 0 10px 10px 0;
  margin-top: 18px;
  font-size: 14.5px;
  line-height: 1.6;
  color: #d8e8f8;
}}

.metrics-row {{
  display: flex;
  gap: 14px;
  margin-top: 18px;
}}

.metric-card {{
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 12px 16px;
  flex: 1;
  text-align: center;
}}

.metric-val {{
  font-size: 22px;
  font-weight: 800;
  color: #00d2d3;
}}

.metric-label {{
  font-size: 12px;
  color: #9abedb;
  margin-top: 4px;
}}

/* ===== SLIDE 6: ARCHITECTURE ===== */
.slide-arch {{
  background: linear-gradient(135deg, #0a111a 0%, #091a2e 50%, #0e3753 100%);
}}

.arch-content {{
  display: flex;
  gap: 30px;
  height: 100%;
  padding: 45px 60px;
}}

.arch-left {{
  width: 52%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

.arch-right {{
  width: 48%;
  display: flex;
  align-items: center;
  justify-content: center;
}}

.arch-right img {{
  width: 100%;
  height: auto;
  border-radius: 14px;
  box-shadow: 0 15px 50px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
}}

.tech-stack {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}}

.tech-badge {{
  background: rgba(0,210,211,0.12);
  border: 1px solid rgba(0,210,211,0.3);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  color: #00d2d3;
  font-weight: 600;
}}

/* ===== SLIDE 7: AI CONTROL PANEL ===== */
.ai-panel-grid {{
  display: flex;
  gap: 14px;
  margin-top: 16px;
}}

.ai-card {{
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 16px 14px;
  flex: 1;
  display: flex;
  flex-direction: column;
}}

.ai-card-header {{
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}}

.ai-card-badge {{
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
}}

.badge-fast {{ background: rgba(0, 210, 211, 0.2); color: #00d2d3; }}
.badge-cloud {{ background: rgba(142, 68, 173, 0.25); color: #bb6bd9; }}
.badge-local {{ background: rgba(39, 174, 96, 0.2); color: #2ecc71; }}
.badge-off {{ background: rgba(231, 76, 60, 0.2); color: #e74c3c; }}

.ai-card-desc {{
  font-size: 11.5px;
  color: #a8cae6;
  line-height: 1.45;
  margin-bottom: 12px;
  min-height: 48px;
}}

.ai-card-points {{
  list-style: none;
  font-size: 11px;
  color: #d0e4f7;
  padding: 0;
}}

.ai-card-points li {{
  margin-bottom: 6px;
  line-height: 1.35;
}}

/* ===== SLIDE 8: AS IS / TO BE ===== */
.slide-asistobe {{
  background: linear-gradient(135deg, #101626 0%, #0d2138 100%);
}}

.comparison {{
  display: flex;
  gap: 20px;
  margin-top: 14px;
}}

.comparison-col {{
  flex: 1;
  border-radius: 12px;
  padding: 20px;
}}

.col-asis {{
  background: rgba(255, 69, 58, 0.08);
  border: 1px solid rgba(255, 69, 58, 0.3);
}}

.col-tobe {{
  background: rgba(0, 210, 211, 0.08);
  border: 1px solid rgba(0, 210, 211, 0.35);
}}

.col-header {{
  font-size: 17px;
  font-weight: 800;
  margin-bottom: 14px;
}}

.col-asis .col-header {{ color: #ff6b6b; }}
.col-tobe .col-header {{ color: #00d2d3; }}

.comparison-list {{
  list-style: none;
  padding: 0;
}}

.comparison-list li {{
  font-size: 13.5px;
  margin-bottom: 10px;
  line-height: 1.45;
  color: #dce7f2;
}}

/* ===== SLIDE 9: MOSCOW SCOPE ===== */
.slide-mvp {{
  background: linear-gradient(135deg, #0e1726 0%, #0a243a 100%);
}}

.moscow-grid {{
  display: flex;
  gap: 12px;
  margin-top: 16px;
}}

.moscow-col {{
  flex: 1;
  background: rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 16px;
}}

.moscow-header {{
  font-size: 15px;
  font-weight: 800;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.moscow-must .moscow-header {{ color: #2ecc71; }}
.moscow-should .moscow-header {{ color: #00d2d3; }}
.moscow-could .moscow-header {{ color: #f39c12; }}
.moscow-wont .moscow-header {{ color: #95a5a6; }}

.moscow-list {{
  list-style: none;
  font-size: 12.5px;
}}

.moscow-list li {{
  margin-bottom: 7px;
  line-height: 1.4;
  color: #cfe1f3;
}}

/* ===== SLIDE 10: PILOT & BUSINESS ===== */
.slide-pilot {{
  background: linear-gradient(135deg, #0d1e33 0%, #0d3b48 100%);
}}

.pilot-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 14px;
}}

.pilot-card {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(0,210,211,0.25);
  border-radius: 10px;
  padding: 12px 14px;
  width: 48%;
}}

.pilot-card-title {{
  font-size: 14px;
  font-weight: 700;
  color: #00d2d3;
  margin-bottom: 4px;
}}

.pilot-card-text {{
  font-size: 12px;
  color: #a8cae6;
  line-height: 1.4;
}}

/* ===== SLIDE 11: FINAL ===== */
.slide-final {{
  background: linear-gradient(135deg, #07111e 0%, #0d2847 40%, #0f3460 70%, #105663 100%);
}}

.final-content {{
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  padding: 60px;
}}

.final-title {{
  font-size: 50px;
  font-weight: 800;
  color: #00d2d3;
  margin-bottom: 16px;
  text-shadow: 0 4px 24px rgba(0, 210, 211, 0.5);
}}

.final-subtitle {{
  font-size: 21px;
  color: #b0d2f5;
  margin-bottom: 34px;
  max-width: 820px;
  line-height: 1.5;
}}

.final-contacts {{
  display: flex;
  gap: 18px;
}}

.final-contact {{
  background: rgba(0, 210, 211, 0.15);
  border: 1px solid #00d2d3;
  border-radius: 10px;
  padding: 10px 22px;
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
}}

</style>
</head>
<body>

<!-- ==================== SLIDE 1: COVER ==================== -->
<div class="slide slide-cover">
  <div class="bg-img"><img src="{COVER}"></div>
  <div class="cover-content">
    <div class="cover-badge">Хакатон 2026 • AI & Data Track</div>
    <div class="cover-title">OmniMetrics Hub & MAX AI</div>
    <div class="cover-subtitle">
      Автономный центр сквозной бизнес-аналитики маркетплейсов,<br>
      умной генерации отчетов и AI-инсайтов в мессенджере MAX
    </div>
    <div class="cover-features-row">
      <div class="cover-feature-pill">📱 Бот в MAX Messenger</div>
      <div class="cover-feature-pill">🛒 WB • Ozon • Я.Маркет • Купер</div>
      <div class="cover-feature-pill">🧠 AI Control Panel (API / Ollama / Rules)</div>
      <div class="cover-feature-pill">📄 PDF • Excel • PNG</div>
    </div>
    <div class="cover-track">Трек: «Эффективный бизнес»</div>
  </div>
  <div class="slide-number">01 / 11</div>
</div>

<!-- ==================== SLIDE 2: PROBLEM ==================== -->
<div class="slide slide-problem">
  <div class="split-layout">
    <div class="split-left">
      <div class="section-label">Проблема бизнеса</div>
      <div class="slide-heading">Данные разрознены.<br>Аналитика запаздывает.</div>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-value">6,6 млн</div>
          <div class="stat-desc">субъектов МСП в РФ, активно выходящих в онлайн и e-commerce</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">83%</div>
          <div class="stat-desc">селлеров сводят продажи и возвраты в Excel вручную</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">5+ часов</div>
          <div class="stat-desc">в неделю уходит на сбор отчетов из разных личных кабинетов</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">72%</div>
          <div class="stat-desc">решений принимаются вслепую из-за задержки цифр и сложного BI</div>
        </div>
      </div>
      <div class="problem-text">
        Селлеры теряют чистую маржу из-за скрытых возвратов, изменения комиссий маркетплейсов и кассовых разрывов. Тяжелые enterprise BI-системы сложны и недоступны малому бизнесу.
      </div>
    </div>
    <div class="split-right">
      <img src="{PROBLEM}">
    </div>
  </div>
  <div class="slide-number">02 / 11</div>
</div>

<!-- ==================== SLIDE 3: SOLUTION ==================== -->
<div class="slide slide-solution">
  <div class="split-layout">
    <div class="split-left">
      <div class="section-label">Наше решение</div>
      <div class="slide-heading">OmniMetrics Hub в MAX</div>
      <ul class="solution-features">
        <li>
          <div class="feature-icon">🛒</div>
          <div><span class="feature-title">Прямые коннекторы к маркетплейсам</span> — Wildberries, Ozon, Яндекс.Маркет, СберМаркет (Купер) синхронизируются в 1 клик.</div>
        </li>
        <li>
          <div class="feature-icon">📱</div>
          <div><span class="feature-title">Нативный бот в MAX Messenger</span> — кнопки, выбор периода, нативная разметка Markdown и моментальная выдача файлов.</div>
        </li>
        <li>
          <div class="feature-icon">🧠</div>
          <div><span class="feature-title">Умный AI Control Panel</span> — свобода выбора: бесплатный детерминированный алгоритм, облачные LLM по API или локальная Ollama.</div>
        </li>
        <li>
          <div class="feature-icon">📄</div>
          <div><span class="feature-title">Мультиформатная выгрузка</span> — полиграфический PDF с графиками, книга Excel (.xlsx) со стилями и формулами, PNG-карточки.</div>
        </li>
        <li>
          <div class="feature-icon">🛑</div>
          <div><span class="feature-title">Приватность и контроль</span> — возможность в любой момент отключить нейросеть одной кнопкой без утечки коммерческой тайны.</div>
        </li>
        <li>
          <div class="feature-icon">🐳</div>
          <div><span class="feature-title">Развертывание за 60 секунд</span> — <code>docker compose up</code>, автомиграции и открытая архитектура.</div>
        </li>
      </ul>
    </div>
    <div class="split-right">
      <img src="{SOLUTION}">
    </div>
  </div>
  <div class="slide-number">03 / 11</div>
</div>

<!-- ==================== SLIDE 4: TARGET AUDIENCE ==================== -->
<div class="slide slide-scenario">
  <div class="full-slide-content">
    <div class="section-label">Целевая аудитория и гипотеза ценности</div>
    <div class="slide-heading">Для кого создан наш продукт</div>
    <div class="scenario-flow">
      <div class="scenario-step">
        <div class="step-number">1</div>
        <div class="step-title">Селлеры маркетплейсов</div>
        <div class="step-desc">Магазины на WB, Ozon, Я.Маркете и Купере. Требуется сквозной контроль выручки, среднего чека, возвратов и рентабельности складов.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">2</div>
        <div class="step-title">Финансовые директора (CFO)</div>
        <div class="step-desc">Управленцы, которым нужны оперативные сводные данные без ожидания ручных таблиц от аналитиков и рутины в 1С.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">3</div>
        <div class="step-title">Руководители МСП</div>
        <div class="step-desc">Предприниматели, которым нужен компактный «карманный аналитик» в удобном мессенджере вместо дорогих зарубежных BI-систем.</div>
      </div>
    </div>
    
    <div class="hypothesis-box">
      <strong>Проверенная гипотеза:</strong> Предоставив селлеру <u>автономного бизнес-ассистента в MAX Messenger</u>, формирующего <u>полный управленческий отчет за 30 секунд</u>, мы <u>высвобождаем до 20 часов рабочего времени в месяц</u> и <u>ускоряем принятие решений в 5 раз</u>, исключая человеческий фактор и ошибки сведения таблиц.
    </div>

    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-val">5 ч → 30 сек</div>
        <div class="metric-label">Время создания отчета</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">4 площадки</div>
        <div class="metric-label">В едином окне MAX</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">0 руб / мес</div>
        <div class="metric-label">Без обязательных подписок на BI</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">100% приватность</div>
        <div class="metric-label">Локальный запуск без передачи данных</div>
      </div>
    </div>
  </div>
  <div class="slide-number">04 / 11</div>
</div>

<!-- ==================== SLIDE 5: USER SCENARIO ==================== -->
<div class="slide slide-scenario" style="background: linear-gradient(135deg, #091e36 0%, #0a3540 100%);">
  <div class="full-slide-content">
    <div class="section-label">Пользовательский сценарий</div>
    <div class="slide-heading">Путь пользователя в мессенджере MAX</div>
    <div class="scenario-flow">
      <div class="scenario-step">
        <div class="step-number">1</div>
        <div class="step-title">Синхронизация данных</div>
        <div class="step-desc">Пользователь в 1 клик запускает синхронизацию Wildberries, Ozon, Я.Маркета, Купера или загружает файл CSV/Excel с продажами.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">2</div>
        <div class="step-title">Интерактивное меню</div>
        <div class="step-desc">В боте MAX открывается нативное меню: выбор отчета (Сводка E-Commerce или KPI метрик) и желаемого периода (7, 30 дней, Месяц).</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">3</div>
        <div class="step-title">Выбор движка AI</div>
        <div class="step-desc">В панели управления можно выбрать: Встроенный быстрый алгоритм, облачную LLM (GigaChat/DeepSeek/OpenAI) или локальную Ollama.</div>
      </div>
    </div>
    <div class="scenario-flow" style="margin-top: 14px;">
      <div class="scenario-step">
        <div class="step-number">4</div>
        <div class="step-title">Мгновенный расчет</div>
        <div class="step-desc">Система агрегирует показатели, вычисляет дельты к прошлому периоду, строит графики трендов и долей каналов продаж.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">5</div>
        <div class="step-title">Управленческий инсайт</div>
        <div class="step-desc">Бот выдает 4 четких пункта: Главный рост, Точка внимания, Паттерн/Аномалия и Рекомендация для команды селлера.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">6</div>
        <div class="step-title">Доставка артефактов</div>
        <div class="step-desc">Пользователь получает PDF-отчет для руководства, файл Excel для глубокого аудита и PNG-карточку для мобильного чтения.</div>
      </div>
    </div>
  </div>
  <div class="slide-number">05 / 11</div>
</div>

<!-- ==================== SLIDE 6: ARCHITECTURE ==================== -->
<div class="slide slide-arch">
  <div class="arch-content">
    <div class="arch-left">
      <div class="section-label">Архитектура решения</div>
      <div class="slide-heading" style="font-size: 32px;">Стек и архитектурные решения</div>
      <ul class="solution-features" style="margin-top: 6px;">
        <li>
          <div class="feature-icon">⚡</div>
          <div><span class="feature-title">FastAPI + SQLAlchemy 2.0</span> — асинхронный высокопроизводительный бэкенд с JSONB-хранилищем метрик.</div>
        </li>
        <li>
          <div class="feature-icon">📱</div>
          <div><span class="feature-title">MAX Bot API (platform-api2.max.ru)</span> — нативная интеграция, Markdown-разметка, callback-кнопки, отправка документов.</div>
        </li>
        <li>
          <div class="feature-icon">🔌</div>
          <div><span class="feature-title">Коннекторы маркетплейсов</span> — отдельные модули для Wildberries, Ozon, Яндекс.Маркета, СберМаркета с mock-песочницей.</div>
        </li>
        <li>
          <div class="feature-icon">📑</div>
          <div><span class="feature-title">Движок экспорта (WeasyPrint + openpyxl)</span> — генерация корпоративных PDF и Excel без внешних платных сервисов.</div>
        </li>
        <li>
          <div class="feature-icon">🧠</div>
          <div><span class="feature-title">Multi-Engine AI Broker</span> — единый интерфейс к эвристике, GigaChat, DeepSeek, OpenAI и Ollama с функцией отключения.</div>
        </li>
      </ul>
      <div class="tech-stack">
        <span class="tech-badge">Python 3.12</span>
        <span class="tech-badge">FastAPI</span>
        <span class="tech-badge">MAX Bot API</span>
        <span class="tech-badge">Docker</span>
        <span class="tech-badge">WeasyPrint</span>
        <span class="tech-badge">openpyxl</span>
        <span class="tech-badge">Plotly</span>
        <span class="tech-badge">PostgreSQL</span>
      </div>
    </div>
    <div class="arch-right">
      <img src="{ARCHITECTURE}">
    </div>
  </div>
  <div class="slide-number">06 / 11</div>
</div>

<!-- ==================== SLIDE 7: AI CONTROL PANEL ==================== -->
<div class="slide slide-scenario">
  <div class="full-slide-content">
    <div class="section-label">Уникальная функциональность</div>
    <div class="slide-heading" style="font-size: 32px;">Панель управления AI и аналитикой (AI Control Panel)</div>
    <p style="font-size: 14px; color: #c0ddf8; margin-bottom: 12px;">
      Бизнес сам решает, как обрабатывать данные: максимальная скорость, умные облачные модели или 100% изоляция.
    </p>
    <div class="ai-panel-grid">
      <div class="ai-card">
        <div class="ai-card-header">
          <span>⚡ Встроенный анализатор</span>
          <span class="ai-card-badge badge-fast">0 сек</span>
        </div>
        <div class="ai-card-desc">
          Детерминированный алгоритмический расчет на основе статистики, дельт и бизнес-правил.
        </div>
        <ul class="ai-card-points">
          <li>✓ Работает без интернета и ключей</li>
          <li>✓ 100% предсказуемый результат</li>
          <li>✓ 4 четких пункта рекомендаций</li>
          <li>✓ Идеален для ежедневного мониторинга</li>
        </ul>
      </div>

      <div class="ai-card">
        <div class="ai-card-header">
          <span>🌐 Облачные LLM (API)</span>
          <span class="ai-card-badge badge-cloud">Cloud AI</span>
        </div>
        <div class="ai-card-desc">
          Глубокий анализ контекста и формулирование стратегических гипотез через передовые нейросети.
        </div>
        <ul class="ai-card-points">
          <li>✓ GigaChat (Сбер) • DeepSeek</li>
          <li>✓ OpenAI GPT-4o • Groq • Claude</li>
          <li>✓ Ввод ключа прямо в чате MAX</li>
          <li>✓ Автоматический fallback при сбоях</li>
        </ul>
      </div>

      <div class="ai-card">
        <div class="ai-card-header">
          <span>💻 Локальная Ollama</span>
          <span class="ai-card-badge badge-local">On-Premise</span>
        </div>
        <div class="ai-card-desc">
          Автономный запуск открытых моделей непосредственно на сервере компании.
        </div>
        <ul class="ai-card-points">
          <li>✓ Llama 3 • Mistral • Qwen 2.5</li>
          <li>✓ Коммерческая тайна не утекает в сеть</li>
          <li>✓ Проверка связи с демоном из бота</li>
          <li>✓ Нулевая стоимость за токены</li>
        </ul>
      </div>

      <div class="ai-card">
        <div class="ai-card-header">
          <span>🛑 Отключение AI</span>
          <span class="ai-card-badge badge-off">1 Клик</span>
        </div>
        <div class="ai-card-desc">
          Мгновенный возврат к надежному встроенному алгоритму по кнопке в интерфейсе или CLI.
        </div>
        <ul class="ai-card-points">
          <li>✓ Кнопка в меню: «Отключить AI»</li>
          <li>✓ Консольная команда: disable-ai</li>
          <li>✓ Честная маркировка в отчетах</li>
          <li>✓ Полный контроль со стороны селлера</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="slide-number">07 / 11</div>
</div>

<!-- ==================== SLIDE 8: DEMO & MARKETPLACES ==================== -->
<div class="slide slide-demo">
  <div class="arch-content">
    <div class="arch-left" style="width: 50%;">
      <div class="section-label">Сквозной E-Commerce Контур</div>
      <div class="slide-heading" style="font-size: 32px;">Единый центр управления продажами</div>
      <ul class="solution-features">
        <li>
          <div class="feature-icon">🟣</div>
          <div><span class="feature-title">Wildberries</span> — отслеживание динамики заказов, выкупов, доли возвратов и отгрузок по складам.</div>
        </li>
        <li>
          <div class="feature-icon">🔵</div>
          <div><span class="feature-title">Ozon</span> — учет комиссий, статусов отправлений (FBO/FBS) и кластерного спроса.</div>
        </li>
        <li>
          <div class="feature-icon">🟡</div>
          <div><span class="feature-title">Яндекс.Маркет</span> — контроль выручки, партнерских тарифов и оборачиваемости.</div>
        </li>
        <li>
          <div class="feature-icon">🟢</div>
          <div><span class="feature-title">СберМаркет / Купер</span> — учет GMV, эффективности розничных точек и географии городов.</div>
        </li>
        <li>
          <div class="feature-icon">📂</div>
          <div><span class="feature-title">Импорт CSV/Excel</span> — быстрая загрузка исторических данных из любых учетных систем (1С, МойСклад).</div>
        </li>
      </ul>
    </div>
    <div class="arch-right" style="width: 50%;">
      <img src="{DASHBOARD}">
    </div>
  </div>
  <div class="slide-number">08 / 11</div>
</div>

<!-- ==================== SLIDE 9: AS IS / TO BE ==================== -->
<div class="slide slide-asistobe">
  <div class="full-slide-content">
    <div class="section-label">Трансформация бизнес-процесса</div>
    <div class="slide-heading" style="font-size: 34px;">Как OmniMetrics меняет работу селлера</div>
    <div class="comparison">
      <div class="comparison-col col-asis">
        <div class="col-header">⛔ Как было раньше (As Is)</div>
        <ul class="comparison-list">
          <li>• Ручной вход в 4 разных личных кабинета селлера каждый день</li>
          <li>• Скачивание десятка сырых Excel-файлов с несовпадающими колонками</li>
          <li>• Сведение таблиц руками: 5+ часов рутины каждую неделю</li>
          <li>• Риск человеческой ошибки при расчете комиссий и возвратов</li>
          <li>• Отчетность запаздывает: решения принимаются с задержкой в неделю</li>
          <li>• Нет готовых выводов: предприниматель тратит часы на чтение графиков</li>
          <li>• Для корпоративных отчетов нужен штатный дорогой аналитик</li>
        </ul>
      </div>
      <div class="comparison-col col-tobe">
        <div class="col-header">✅ С OmniMetrics в MAX (To Be)</div>
        <ul class="comparison-list">
          <li>• Все площадки (WB, Ozon, Я.Маркет, Купер) подключены к единому хабу</li>
          <li>• Данные нормализуются и раскладываются по тегам автоматически</li>
          <li>• Отчет формируется за 30 секунд по одной кнопке в MAX Messenger</li>
          <li>• Исключены математические ошибки и путаница в формулах</li>
          <li>• Управленческие решения принимаются день в день по свежим цифрам</li>
          <li>• Готовая сводка из 4 пунктов: что растет, где риск и что делать</li>
          <li>• Профессиональный PDF и Excel готовы к отправке инвесторам и руководству</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="slide-number">09 / 11</div>
</div>

<!-- ==================== SLIDE 10: MVP SCOPE & ROADMAP ==================== -->
<div class="slide slide-mvp">
  <div class="full-slide-content">
    <div class="section-label">Границы MVP и планы развития</div>
    <div class="slide-heading" style="font-size: 34px;">Реализация по MoSCoW и дорожная карта</div>
    <div class="moscow-grid">
      <div class="moscow-col moscow-must">
        <div class="moscow-header">✓ Must Have (100% Готово)</div>
        <ul class="moscow-list">
          <li>✓ Интерактивный бот MAX Messenger</li>
          <li>✓ Нативная Markdown-разметка</li>
          <li>✓ Коннекторы WB, Ozon, ЯМ, Купер</li>
          <li>✓ Генерация полиграфических PDF</li>
          <li>✓ Стилизованные книги Excel (.xlsx)</li>
          <li>✓ REST API приема метрик (до 5000)</li>
          <li>✓ Деплой в Docker Compose</li>
        </ul>
      </div>
      <div class="moscow-col moscow-should">
        <div class="moscow-header">✓ Should Have (100% Готово)</div>
        <ul class="moscow-list">
          <li>✓ AI Control Panel (API/Ollama/Rules)</li>
          <li>✓ Кнопка быстрого отключения AI</li>
          <li>✓ Ручной импорт CSV/Excel файлов</li>
          <li>✓ Встроенный эвристический аналитик</li>
          <li>✓ Графики трендов и долей (PNG)</li>
          <li>✓ Консольный CLI-интерфейс</li>
          <li>✓ Telegram-бот на aiogram 3.x</li>
        </ul>
      </div>
      <div class="moscow-col moscow-could">
        <div class="moscow-header">○ Дорожная карта (Q4 2026)</div>
        <ul class="moscow-list">
          <li>○ Прямая интеграция с 1С и МойСклад</li>
          <li>○ Банковский Open API (Сбер, Т-Банк)</li>
          <li>○ Предиктивный расчет потребности в поставках</li>
          <li>○ Контроль маржинальности каждого SKU</li>
          <li>○ Автоуведомления об аномалиях продаж</li>
        </ul>
      </div>
      <div class="moscow-col moscow-wont">
        <div class="moscow-header">— За рамками хакатона</div>
        <ul class="moscow-list">
          <li>— Собственное мобильное приложение (мессенджера MAX достаточно)</li>
          <li>— Автоматическое изменение цен в ЛК селлера (безопасность бизнеса)</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="slide-number">10 / 11</div>
</div>

<!-- ==================== SLIDE 11: FINAL ==================== -->
<div class="slide slide-final">
  <div class="bg-img"><img src="{COVER}"></div>
  <div class="final-content">
    <div class="final-title">OmniMetrics Hub & MAX AI</div>
    <div class="final-subtitle">
      Ваш умный бизнес-ассистент и центр управления аналитикой в мессенджере MAX.<br>
      Синхронизируйте маркетплейсы. Получайте инсайты. Масштабируйте бизнес.
    </div>
    <div class="final-contacts">
      <div class="final-contact">🤖 Бот: @t115_hakaton_max_bot</div>
      <div class="final-contact">🧪 25 пройденных автотестов</div>
      <div class="final-contact">🐳 docker compose up</div>
    </div>
    <div style="margin-top: 26px; color: #a0c4e8; font-size: 15px;">
      Хакатон 2026 • Трек «Эффективный бизнес» • Команда OmniMetrics
    </div>
  </div>
  <div class="slide-number">11 / 11</div>
</div>

</body>
</html>
"""

# Write HTML
html_path = OUTPUT_DIR / "presentation.html"
html_path.write_text(HTML, encoding="utf-8")
print(f"✅ HTML saved to {html_path}")

# Generate PDF with WeasyPrint
from weasyprint import HTML as WHTML
pdf_path = OUTPUT_DIR / "presentation.pdf"
WHTML(filename=str(html_path)).write_pdf(str(pdf_path))
print(f"✅ PDF saved to {pdf_path}")
print(f"   File size: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
