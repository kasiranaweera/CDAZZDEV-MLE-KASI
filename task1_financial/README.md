<div align="center">

# Task 1 — Financial AI: LLM-Powered Equity Research Pipeline

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kasiranaweera/CDAZZDEV-MLE-KASI/blob/main/task1_financial/CDAZZDEV_Task1_Financial_AI.ipynb)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA--3.3--70b-orange)](https://console.groq.com)
[![Pydantic](https://img.shields.io/badge/validation-Pydantic%20v2-red)](https://docs.pydantic.dev)

</dev>

---

## Overview

An end-to-end equity research pipeline that fetches real-time market data, computes five technical indicators from first principles, analyses news sentiment via LLM, and generates a structured Buy/Hold/Sell trade signal — all validated with Pydantic schemas and rendered as a styled HTML research brief.

---



## Features

### Task 1A — Data Pipeline

**OHLCV Fetch — 3-level fallback chain:**
1. `yfinance` with `curl_cffi` (bot-detection bypass)
2. Stooq direct HTTP
3. Alpha Vantage compact (~100 days)

**Technical Indicators — computed from raw NumPy/Pandas (no TA-Lib):**

| Indicator | Parameters | Notes |
|-----------|-----------|-------|
| SMA-50 | 50-day rolling mean | Golden/death cross detection |
| SMA-200 | 200-day rolling mean | First 200 rows NaN — expected |
| RSI | Period 14 | Wilder's EWM smoothing (alpha=1/14, adjust=False) |
| MACD | (12, 26, 9) | Signal line + histogram |
| Bollinger Bands | 20-period, 2σ | Upper, mid, lower bands |

**News Headlines:**
- 15 recent headlines via Yahoo Finance RSS → Google News RSS → Alpha Vantage News API fallback
- Deduplication and null handling throughout

**Summary Dictionary fields:** `current_price`, `52w_high`, `52w_low`, `pe_ratio`, `ytd_return`, `momentum_signal`

---

### Task 1B — LLM Analysis

**Model:** Groq `llama-3.3-70b-versatile`

**Sentiment Analysis (per headline):**

```json
{
  "headline": "...",
  "sentiment": "positive | negative | neutral",
  "confidence": 0.0–1.0,
  "brief_reason": "..."
}
```

Aggregated into a single weighted overall sentiment score.

**Trade Signal:**

```json
{
  "signal": "Buy | Hold | Sell",
  "confidence": 0.0–1.0,
  "justification": "3–5 sentences reasoning over indicator combinations",
  "key_factors": ["..."],
  "risk_level": "Low | Medium | High"
}
```

**Structured Output Validation:**
- All LLM responses validated via Pydantic v2 schemas with custom field validators
- Validation failures caught, logged, and handled gracefully — pipeline never halts on a bad response
- Prompts defined as module-level constants, fully separated from business logic

---

## Output Files

| File | Description |
|------|-------------|
| `chart_technical.png` | Multi-panel matplotlib chart: price + SMAs + Bollinger Bands, RSI, MACD |
| `equity_report.html` | Styled HTML equity research brief with embedded chart, indicator table, sentiment summary, and trade recommendation |

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TICKER` | `AAPL` | Stock ticker symbol |
| `PERIOD` | `2y` | Historical data period |
| `NEWS_COUNT` | `15` | Number of headlines to fetch |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model for LLM calls |

---

## API Keys

| Key | Required | How to set |
|-----|----------|-----------|
| `GROQ_API_KEY` | ✅ Yes | Add to Colab Secrets (🔑 sidebar) or set as env var |
| `AV_API_KEY` | ❌ Optional | Alpha Vantage fallback — [get free key](https://www.alphavantage.co/support/#api-key) |

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Market data | yfinance · curl_cffi · requests |
| Indicators | pandas · numpy |
| LLM inference | Groq SDK (`llama-3.3-70b-versatile`) |
| Structured output | Pydantic v2 |
| Charting | matplotlib |
| Reporting | Jinja2 / HTML |

---



## Known Limitations

- SMA-200 warmup: first 200 rows carry NaN — expected and documented in notebook output
- `yfinance` may be blocked intermittently; Stooq and Alpha Vantage fallbacks handle this
- Alpha Vantage free tier is limited to ~100 days of daily data (compact output)

---

← [Back to root README](../README.md)