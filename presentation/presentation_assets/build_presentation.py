#!/usr/bin/env python3
"""Build a beautiful PDF presentation for OmniMetrics Hub (Russian)."""

import base64
import os
from pathlib import Path

ASSETS = Path("/root/presentation_assets")

def img_b64(name: str) -> str:
    """Convert image file to base64 data URI."""
    path = ASSETS / name
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:image/jpeg;base64,{b64}"

# Load all images
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
  background: linear-gradient(135deg, #0a1628 0%, #0d2847 40%, #0f3460 70%, #16697a 100%);
}}

.bg-img {{
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  opacity: 0.25;
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
  padding: 60px;
}}

.cover-badge {{
  background: rgba(0, 210, 211, 0.15);
  border: 2px solid #00d2d3;
  border-radius: 30px;
  padding: 8px 28px;
  font-size: 16px;
  color: #00d2d3;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 30px;
}}

.cover-title {{
  font-size: 58px;
  font-weight: 800;
  background: linear-gradient(90deg, #ffffff 0%, #00d2d3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
  line-height: 1.15;
}}

.cover-subtitle {{
  font-size: 24px;
  color: #a0c4e8;
  margin-bottom: 40px;
  max-width: 800px;
}}

.cover-track {{
  background: linear-gradient(90deg, #00d2d3, #0f3460);
  padding: 12px 40px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}}

/* ===== SLIDE 2: PROBLEM ===== */
.slide-problem {{
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}}

.split-layout {{
  display: flex;
  height: 100%;
}}

.split-left {{
  width: 55%;
  padding: 50px 40px 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

.split-right {{
  width: 45%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
}}

.split-right img {{
  width: 100%;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}}

.slide-number {{
  position: absolute;
  bottom: 20px;
  right: 40px;
  font-size: 14px;
  color: rgba(255,255,255,0.3);
}}

.section-label {{
  font-size: 13px;
  color: #00d2d3;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 12px;
  font-weight: 600;
}}

.slide-heading {{
  font-size: 38px;
  font-weight: 800;
  margin-bottom: 24px;
  line-height: 1.2;
}}

.stat-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}}

.stat-card {{
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 14px 18px;
  width: 47%;
}}

.stat-value {{
  font-size: 28px;
  font-weight: 800;
  color: #00d2d3;
}}

.stat-desc {{
  font-size: 12px;
  color: #a0c4e8;
  margin-top: 4px;
}}

.problem-text {{
  font-size: 15px;
  color: #cdd9e5;
  line-height: 1.6;
}}

/* ===== SLIDE 3: SOLUTION ===== */
.slide-solution {{
  background: linear-gradient(135deg, #0a2342 0%, #0d4449 50%, #126e72 100%);
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
  margin-bottom: 14px;
  font-size: 15px;
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

/* ===== SLIDE 4: SCENARIO ===== */
.slide-scenario {{
  background: linear-gradient(135deg, #1a1a2e 0%, #0d2847 100%);
}}

.scenario-flow {{
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}}

.scenario-step {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(0,210,211,0.3);
  border-radius: 14px;
  padding: 18px;
  width: 30%;
  position: relative;
}}

.step-number {{
  background: linear-gradient(135deg, #00d2d3, #0f3460);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  margin-bottom: 10px;
}}

.step-title {{
  font-size: 16px;
  font-weight: 700;
  color: #00d2d3;
  margin-bottom: 6px;
}}

.step-desc {{
  font-size: 13px;
  color: #a0c4e8;
  line-height: 1.5;
}}

.full-slide-content {{
  padding: 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 100%;
}}

/* ===== SLIDE 5: ARCHITECTURE ===== */
.slide-arch {{
  background: linear-gradient(135deg, #0d1117 0%, #0a1628 50%, #0f3460 100%);
}}

.arch-content {{
  display: flex;
  gap: 30px;
  height: 100%;
  padding: 50px 60px;
}}

.arch-left {{
  width: 48%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

.arch-right {{
  width: 52%;
  display: flex;
  align-items: center;
  justify-content: center;
}}

.arch-right img {{
  width: 100%;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 15px 50px rgba(0,0,0,0.5);
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
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 12px;
  color: #00d2d3;
  font-weight: 600;
}}

/* ===== SLIDE 6: DEMO ===== */
.slide-demo {{
  background: linear-gradient(135deg, #0a1628 0%, #1a1a2e 100%);
}}

.demo-content {{
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  padding: 40px 60px;
}}

.demo-img {{
  width: 90%;
  margin-top: 20px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  border: 2px solid rgba(0,210,211,0.2);
}}

/* ===== SLIDE 7: AS IS / TO BE ===== */
.slide-asistobe {{
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}}

.comparison {{
  display: flex;
  gap: 20px;
  margin-top: 20px;
  flex: 1;
}}

.comparison-col {{
  width: 50%;
  border-radius: 16px;
  padding: 24px;
}}

.col-asis {{
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
}}

.col-tobe {{
  background: rgba(0, 210, 211, 0.1);
  border: 1px solid rgba(0, 210, 211, 0.3);
}}

.col-header {{
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(255,255,255,0.1);
}}

.col-asis .col-header {{ color: #e74c3c; }}
.col-tobe .col-header {{ color: #00d2d3; }}

.comparison-list {{
  list-style: none;
  padding: 0;
}}

.comparison-list li {{
  font-size: 14px;
  color: #cdd9e5;
  padding: 6px 0;
  padding-left: 24px;
  position: relative;
  line-height: 1.5;
}}

.col-asis .comparison-list li::before {{
  content: "✗";
  position: absolute;
  left: 0;
  color: #e74c3c;
  font-weight: 700;
}}

.col-tobe .comparison-list li::before {{
  content: "✓";
  position: absolute;
  left: 0;
  color: #00d2d3;
  font-weight: 700;
}}

/* ===== SLIDE 8: SCALING ===== */
.slide-scaling {{
  background: linear-gradient(135deg, #0a2342 0%, #0d4449 100%);
}}

/* ===== SLIDE 9: PILOT ===== */
.slide-pilot {{
  background: linear-gradient(135deg, #1a1a2e 0%, #2d1b69 50%, #0f3460 100%);
}}

.pilot-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 16px;
}}

.pilot-card {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 16px 20px;
  width: 31%;
}}

.pilot-card-title {{
  font-size: 14px;
  font-weight: 700;
  color: #00d2d3;
  margin-bottom: 8px;
}}

.pilot-card-text {{
  font-size: 12px;
  color: #a0c4e8;
  line-height: 1.5;
}}

/* ===== SLIDE 10: MVP SCOPE ===== */
.slide-mvp {{
  background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2847 100%);
}}

.moscow-grid {{
  display: flex;
  gap: 14px;
  margin-top: 16px;
}}

.moscow-col {{
  border-radius: 12px;
  padding: 18px;
  width: 25%;
}}

.moscow-must {{ background: rgba(0,210,211,0.12); border: 1px solid rgba(0,210,211,0.3); }}
.moscow-should {{ background: rgba(52,152,219,0.12); border: 1px solid rgba(52,152,219,0.3); }}
.moscow-could {{ background: rgba(241,196,15,0.12); border: 1px solid rgba(241,196,15,0.3); }}
.moscow-wont {{ background: rgba(149,165,166,0.1); border: 1px solid rgba(149,165,166,0.3); }}

.moscow-header {{
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(255,255,255,0.1);
}}

.moscow-must .moscow-header {{ color: #00d2d3; }}
.moscow-should .moscow-header {{ color: #3498db; }}
.moscow-could .moscow-header {{ color: #f1c40f; }}
.moscow-wont .moscow-header {{ color: #95a5a6; }}

.moscow-list {{
  list-style: none;
  padding: 0;
}}

.moscow-list li {{
  font-size: 12px;
  color: #cdd9e5;
  padding: 4px 0;
  line-height: 1.4;
}}

/* ===== SLIDE 11: FINAL ===== */
.slide-final {{
  background: linear-gradient(135deg, #0a1628 0%, #0d2847 40%, #0f3460 70%, #16697a 100%);
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
  font-size: 52px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 20px;
}}

.final-subtitle {{
  font-size: 22px;
  color: #a0c4e8;
  max-width: 700px;
  margin-bottom: 30px;
}}

.final-contacts {{
  display: flex;
  gap: 30px;
}}

.final-contact {{
  background: rgba(0,210,211,0.1);
  border: 1px solid rgba(0,210,211,0.3);
  border-radius: 12px;
  padding: 14px 28px;
  color: #00d2d3;
  font-size: 16px;
  font-weight: 600;
}}

/* ===== HYPOTHESIS ===== */
.hypothesis-box {{
  background: rgba(0,210,211,0.08);
  border-left: 4px solid #00d2d3;
  border-radius: 0 12px 12px 0;
  padding: 16px 20px;
  margin: 16px 0;
  font-size: 15px;
  color: #e0e8f0;
  line-height: 1.6;
  font-style: italic;
}}

.metrics-row {{
  display: flex;
  gap: 12px;
  margin-top: 14px;
}}

.metric-card {{
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 12px 16px;
  text-align: center;
  flex: 1;
}}

.metric-val {{
  font-size: 22px;
  font-weight: 800;
  color: #00d2d3;
}}

.metric-label {{
  font-size: 11px;
  color: #a0c4e8;
  margin-top: 3px;
}}

</style>
</head>
<body>

<!-- ==================== SLIDE 1: COVER ==================== -->
<div class="slide slide-cover">
  <div class="bg-img"><img src="{COVER}"></div>
  <div class="cover-content">
    <div class="cover-badge">Хакатон 2026</div>
    <div class="cover-title">OmniMetrics Hub</div>
    <div class="cover-subtitle">
      Единая платформа бизнес-аналитики с AI-инсайтами<br>
      и доставкой отчётов через Telegram-бота
    </div>
    <div class="cover-track">Трек: Эффективный бизнес</div>
  </div>
  <div class="slide-number">01 / 11</div>
</div>

<!-- ==================== SLIDE 2: PROBLEM ==================== -->
<div class="slide slide-problem">
  <div class="split-layout">
    <div class="split-left">
      <div class="section-label">Проблема</div>
      <div class="slide-heading">Данные есть.<br>Понимания — нет.</div>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-value">6,6 млн</div>
          <div class="stat-desc">субъектов МСП зарегистрировано в России (2026)</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">83%</div>
          <div class="stat-desc">предпринимателей ведут учёт в Excel вручную</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">5+ часов</div>
          <div class="stat-desc">в неделю тратится на сбор и подготовку отчётов</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">72%</div>
          <div class="stat-desc">принимают решения без аналитической поддержки</div>
        </div>
      </div>
      <div class="problem-text">
        Малый и средний бизнес накапливает данные из десятков источников, но не имеет 
        простого инструмента для их агрегации, визуализации и получения рекомендаций.
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
      <div class="slide-heading">OmniMetrics Hub</div>
      <ul class="solution-features">
        <li>
          <div class="feature-icon">📊</div>
          <div><span class="feature-title">Универсальный REST API</span> — загрузите любые числовые метрики с гибкими тегами, без миграций БД</div>
        </li>
        <li>
          <div class="feature-icon">🤖</div>
          <div><span class="feature-title">Telegram-бот</span> — получайте отчёты прямо в мессенджере через удобное inline-меню</div>
        </li>
        <li>
          <div class="feature-icon">🧠</div>
          <div><span class="feature-title">AI Executive Briefing</span> — искусственный интеллект анализирует тренды и даёт рекомендации</div>
        </li>
        <li>
          <div class="feature-icon">📄</div>
          <div><span class="feature-title">Мультиформат</span> — PDF, Excel, PNG-графики, Google Sheets — всё в одном</div>
        </li>
        <li>
          <div class="feature-icon">🔌</div>
          <div><span class="feature-title">Плагинная архитектура</span> — добавьте свой тип отчёта, просто создав Python-файл</div>
        </li>
        <li>
          <div class="feature-icon">🐳</div>
          <div><span class="feature-title">Одна команда</span> — <code>docker compose up</code> и платформа работает</div>
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
    <div class="section-label">Целевая аудитория</div>
    <div class="slide-heading">Для кого мы создаём продукт</div>
    <div class="scenario-flow">
      <div class="scenario-step">
        <div class="step-number">1</div>
        <div class="step-title">Владельцы e-commerce</div>
        <div class="step-desc">Интернет-магазины и маркетплейсы, которые хотят отслеживать выручку, заказы, конверсию, средний чек и получать рекомендации по росту</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">2</div>
        <div class="step-title">Операционные менеджеры</div>
        <div class="step-desc">Сотрудники, отвечающие за KPI, которым нужны автоматические отчёты по расписанию без ручного сбора данных из разных систем</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">3</div>
        <div class="step-title">Руководители МСП</div>
        <div class="step-desc">Предприниматели, которым нужна «панель управления» бизнесом в привычном мессенджере, а не сложные BI-системы</div>
      </div>
    </div>
    
    <div class="hypothesis-box">
      <strong>Гипотеза:</strong> Если мы поможем <u>предпринимателю МСП</u> получить 
      <u>аналитический отчёт с AI-рекомендациями</u> через <u>Telegram-бота за 30 секунд</u>, 
      то <u>время принятия решений</u> сократится в <u>5 раз</u>, потому что данные из различных 
      источников будут автоматически агрегированы и визуализированы.
    </div>

    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-val">5 ч → 30 сек</div>
        <div class="metric-label">Время создания отчёта</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">0 → 100%</div>
        <div class="metric-label">Доля автоматизации</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">−80%</div>
        <div class="metric-label">Ручных действий</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">+AI</div>
        <div class="metric-label">Рекомендации к данным</div>
      </div>
    </div>
  </div>
  <div class="slide-number">04 / 11</div>
</div>

<!-- ==================== SLIDE 5: USER SCENARIO ==================== -->
<div class="slide slide-scenario" style="background: linear-gradient(135deg, #0a2342 0%, #0d4449 100%);">
  <div class="full-slide-content">
    <div class="section-label">Пользовательский сценарий</div>
    <div class="slide-heading">Путь пользователя от данных до решения</div>
    <div class="scenario-flow">
      <div class="scenario-step">
        <div class="step-number">1</div>
        <div class="step-title">Загрузка метрик</div>
        <div class="step-desc">Предприниматель отправляет метрики через REST API из CRM, 1С, маркетплейса или вручную. Поддержка единичной и пакетной загрузки до 5 000 записей.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">2</div>
        <div class="step-title">Запрос отчёта</div>
        <div class="step-desc">В Telegram пользователь нажимает кнопку «📊 Отчёты», выбирает тип (общая аналитика или e-commerce) и период (7/30/90 дней).</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">3</div>
        <div class="step-title">Генерация</div>
        <div class="step-desc">Система агрегирует данные, строит графики, формирует таблицы и запрашивает AI-анализ трендов и аномалий.</div>
      </div>
    </div>
    <div class="scenario-flow" style="margin-top: 14px;">
      <div class="scenario-step">
        <div class="step-number">4</div>
        <div class="step-title">Доставка результата</div>
        <div class="step-desc">Бот отправляет: PDF-отчёт со стилизованными графиками, Excel-таблицу с данными, PNG-превью для быстрого просмотра.</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">5</div>
        <div class="step-title">AI-брифинг</div>
        <div class="step-desc">Текстовый блок с ключевыми выводами: «Выручка выросла на 12%, но конверсия снижается — рекомендуем оптимизировать воронку».</div>
      </div>
      <div class="scenario-step">
        <div class="step-number">6</div>
        <div class="step-title">Автоматизация</div>
        <div class="step-desc">Настройка расписания: ежедневные или еженедельные отчёты автоматически приходят в Telegram без действий пользователя.</div>
      </div>
    </div>
  </div>
  <div class="slide-number">05 / 11</div>
</div>

<!-- ==================== SLIDE 6: ARCHITECTURE ==================== -->
<div class="slide slide-arch">
  <div class="arch-content">
    <div class="arch-left">
      <div class="section-label">Архитектура</div>
      <div class="slide-heading" style="font-size: 34px;">Технологический стек</div>
      <ul class="solution-features" style="margin-top: 10px;">
        <li>
          <div class="feature-icon">⚡</div>
          <div><span class="feature-title">FastAPI</span> — асинхронный REST API с Pydantic v2 валидацией</div>
        </li>
        <li>
          <div class="feature-icon">🗄</div>
          <div><span class="feature-title">PostgreSQL / SQLite</span> — JSONB хранение тегов без миграций</div>
        </li>
        <li>
          <div class="feature-icon">📱</div>
          <div><span class="feature-title">aiogram 3.x</span> — Telegram-бот с inline-клавиатурой и авторизацией</div>
        </li>
        <li>
          <div class="feature-icon">📈</div>
          <div><span class="feature-title">Plotly + Matplotlib</span> — авто-выбор типа визуализации</div>
        </li>
        <li>
          <div class="feature-icon">🤖</div>
          <div><span class="feature-title">LLM (OpenAI/Anthropic/Ollama)</span> — AI-анализ с привязкой к источникам</div>
        </li>
      </ul>
      <div class="tech-stack">
        <span class="tech-badge">Python 3.12</span>
        <span class="tech-badge">Docker</span>
        <span class="tech-badge">SQLAlchemy 2.0</span>
        <span class="tech-badge">WeasyPrint</span>
        <span class="tech-badge">openpyxl</span>
        <span class="tech-badge">APScheduler</span>
        <span class="tech-badge">Jinja2</span>
        <span class="tech-badge">Pydantic v2</span>
      </div>
    </div>
    <div class="arch-right">
      <img src="{ARCHITECTURE}">
    </div>
  </div>
  <div class="slide-number">06 / 11</div>
</div>

<!-- ==================== SLIDE 7: DEMO ==================== -->
<div class="slide slide-demo">
  <div class="demo-content">
    <div class="section-label">Демонстрация</div>
    <div class="slide-heading" style="font-size: 34px;">Работающий MVP: 1 595 метрик за 60 дней</div>
    <img class="demo-img" src="{DASHBOARD}">
  </div>
  <div class="slide-number">07 / 11</div>
</div>

<!-- ==================== SLIDE 8: AS IS / TO BE ==================== -->
<div class="slide slide-asistobe">
  <div class="full-slide-content">
    <div class="section-label">Трансформация процесса</div>
    <div class="slide-heading" style="font-size: 34px;">Как меняется работа с данными</div>
    <div class="comparison">
      <div class="comparison-col col-asis">
        <div class="col-header">⛔ Как сейчас (As Is)</div>
        <ul class="comparison-list">
          <li>Данные хранятся в разрозненных Excel-файлах</li>
          <li>Ручной сбор из CRM, маркетплейсов, бухгалтерии</li>
          <li>Отчёты готовятся вручную 5+ часов в неделю</li>
          <li>Нет единой визуализации трендов</li>
          <li>Решения принимаются «на глаз» без аналитики</li>
          <li>Нет оповещений об аномалиях и отклонениях</li>
          <li>Для BI-системы нужен дорогой специалист</li>
          <li>Данные устаревают к моменту анализа</li>
        </ul>
      </div>
      <div class="comparison-col col-tobe">
        <div class="col-header">✅ С OmniMetrics (To Be)</div>
        <ul class="comparison-list">
          <li>Единый REST API для всех источников данных</li>
          <li>Автоматическая агрегация при загрузке через API</li>
          <li>Отчёт генерируется за 30 секунд по кнопке в Telegram</li>
          <li>Интерактивные графики с авто-выбором типа</li>
          <li>AI-рекомендации на основе анализа трендов</li>
          <li>Автоматические отчёты по расписанию</li>
          <li>Запуск одной командой: docker compose up</li>
          <li>Актуальные данные в реальном времени</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="slide-number">08 / 11</div>
</div>

<!-- ==================== SLIDE 9: MVP SCOPE ==================== -->
<div class="slide slide-mvp">
  <div class="full-slide-content">
    <div class="section-label">Границы MVP</div>
    <div class="slide-heading" style="font-size: 34px;">Приоритизация по MoSCoW</div>
    <div class="moscow-grid">
      <div class="moscow-col moscow-must">
        <div class="moscow-header">Must Have</div>
        <ul class="moscow-list">
          <li>✓ REST API (загрузка метрик)</li>
          <li>✓ Пакетная загрузка до 5000</li>
          <li>✓ Telegram-бот с авторизацией</li>
          <li>✓ Генерация PDF-отчётов</li>
          <li>✓ Визуализация графиками</li>
          <li>✓ 2 встроенных типа отчётов</li>
          <li>✓ Docker-деплой</li>
        </ul>
      </div>
      <div class="moscow-col moscow-should">
        <div class="moscow-header">Should Have</div>
        <ul class="moscow-list">
          <li>✓ Excel-экспорт</li>
          <li>✓ PNG-превью графиков</li>
          <li>✓ AI Executive Briefing</li>
          <li>✓ Inline-клавиатура</li>
          <li>✓ Выбор периода</li>
          <li>✓ Автоматическое расписание</li>
          <li>✓ Плагинная архитектура</li>
        </ul>
      </div>
      <div class="moscow-col moscow-could">
        <div class="moscow-header">Could Have</div>
        <ul class="moscow-list">
          <li>○ Google Sheets синхронизация</li>
          <li>○ Webhook-уведомления</li>
          <li>○ Мультиязычность</li>
          <li>○ Дашборд-интерфейс</li>
          <li>○ Экспорт в Notion</li>
        </ul>
      </div>
      <div class="moscow-col moscow-wont">
        <div class="moscow-header">Won't Have</div>
        <ul class="moscow-list">
          <li>— Мини-приложение MAX</li>
          <li>— Мультитенантность</li>
          <li>— Пользовательские роли</li>
          <li>— ML-предсказания</li>
          <li>— Мобильное приложение</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="slide-number">09 / 11</div>
</div>

<!-- ==================== SLIDE 10: SCALING & PILOT ==================== -->
<div class="slide slide-pilot">
  <div class="split-layout">
    <div class="split-left">
      <div class="section-label">Масштабирование и пилот</div>
      <div class="slide-heading" style="font-size: 32px;">Путь от MVP к тиражированию</div>
      <div class="pilot-grid">
        <div class="pilot-card">
          <div class="pilot-card-title">🎯 Пилотный запуск</div>
          <div class="pilot-card-text">10-20 предпринимателей e-commerce в одном регионе (Москва/МО). Бесплатный доступ на 3 месяца.</div>
        </div>
        <div class="pilot-card">
          <div class="pilot-card-title">📊 Метрики пилота</div>
          <div class="pilot-card-text">MAU, кол-во отчётов/день, NPS, % удержания, время до первого отчёта.</div>
        </div>
        <div class="pilot-card">
          <div class="pilot-card-title">🔄 Ядро продукта</div>
          <div class="pilot-card-text">API, движок отчётов, AI-анализ, бот — не меняются при масштабировании.</div>
        </div>
        <div class="pilot-card">
          <div class="pilot-card-title">🌍 Адаптация</div>
          <div class="pilot-card-text">Региональные данные, справочники, интеграции с местными системами (1С, МойСклад).</div>
        </div>
        <div class="pilot-card">
          <div class="pilot-card-title">📈 Масштаб</div>
          <div class="pilot-card-text">Розничная торговля → HoReCa → производство → B2B-услуги. Вся Россия.</div>
        </div>
        <div class="pilot-card">
          <div class="pilot-card-title">⚠️ Риски</div>
          <div class="pilot-card-text">Качество данных от пользователей, нагрузка AI при росте, интеграция с legacy-системами.</div>
        </div>
      </div>
    </div>
    <div class="split-right">
      <img src="{PILOT}">
    </div>
  </div>
  <div class="slide-number">10 / 11</div>
</div>

<!-- ==================== SLIDE 11: FINAL ==================== -->
<div class="slide slide-final">
  <div class="bg-img"><img src="{COVER}"></div>
  <div class="final-content">
    <div class="final-title">Спасибо!</div>
    <div class="final-subtitle">
      OmniMetrics Hub — ваш бизнес-аналитик в Telegram.<br>
      Загрузите данные. Получите инсайты. Принимайте решения.
    </div>
    <div class="final-contacts">
      <div class="final-contact">🐳 docker compose up</div>
      <div class="final-contact">📊 1 595 тестовых метрик</div>
      <div class="final-contact">🧪 20 тестов пройдено</div>
    </div>
    <div style="margin-top: 30px; color: #a0c4e8; font-size: 16px;">
      Трек «Эффективный бизнес» • Хакатон 2026
    </div>
  </div>
  <div class="slide-number">11 / 11</div>
</div>

</body>
</html>
"""

# Write HTML
html_path = Path("/root/presentation.html")
html_path.write_text(HTML, encoding="utf-8")
print(f"✅ HTML saved to {html_path}")

# Generate PDF with WeasyPrint
from weasyprint import HTML as WHTML
pdf_path = "/root/presentation.pdf"
WHTML(filename=str(html_path)).write_pdf(pdf_path)
print(f"✅ PDF saved to {pdf_path}")
print(f"   File size: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
