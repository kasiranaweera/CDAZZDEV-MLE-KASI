<div align="center">

# Task 3 — Agentic Workflows: Multi-Agent Financial Research System

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kasiranaweera/CDAZZDEV-MLE-KASI/blob/main/task3_agentic/CDAZZDEV_Task3_Agentic_Workflows.ipynb)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-purple)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLaMA--3.3--70b-orange)](https://console.groq.com)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-green)](https://smith.langchain.com)

</dev>

---

## Overview

A production-grade multi-agent financial research system that autonomously analyses a stock ticker, coordinates two specialised AI agents, and produces a structured 3-section investment research report — with short-term memory, persistent caching, JSONL observability, and a live Streamlit trace dashboard.

**Research query:**
> *"Analyse the current financial health and market sentiment of [TICKER]. Identify the top three risks to its share price over the next 90 days and suggest one data-driven hedge strategy."*

---

## Architecture

```
                        ┌─────────────────────────────┐
                        │         Task 3A             │
                        │   Single LangGraph ReAct    │
                        │   Agent (5 tools)           │
                        │   Observe → Reason → Act    │
                        └─────────────────────────────┘

┌──────────────────┐    Pydantic DataBrief    ┌──────────────────┐
│   Agent A        │ ──────────────────────► │   Agent B        │
│  Data Analyst    │                          │ Research Writer  │
│  get_price_data  │ ◄────────────────────── │  web_search      │
│  calc_volatility │   clarification request  │  get_news        │
│  llm_sentiment   │                          │                  │
└──────────────────┘                          └──────────────────┘
         │                  Task 3B                    │
         └────────────── FinalReport ─────────────────┘

                        Task 3C
              ┌─────────────────────────────┐
              │  Short-term session memory  │
              │  Persistent JSON cache      │
              │  agent_trace.jsonl          │
              │  Streamlit dashboard        │
              │  LangSmith tracing          │
              └─────────────────────────────┘
```

---

## Tools

| Tool | Purpose | Available To |
|------|---------|-------------|
| `get_price_data(ticker, period)` | yfinance OHLCV + SMA, RSI, MACD, Bollinger Bands, P/E, YTD return | Agent A · Task 3A |
| `calculate_volatility(ticker, window)` | Annualised historical volatility, volatility regime, beta vs SPY | Agent A · Task 3A |
| `llm_sentiment(headlines)` | Groq LLaMA-3 per-headline sentiment + weighted aggregate score | Agent A · Task 3A |
| `get_news(ticker, n)` | Yahoo Finance headlines — structured list | Agent B · Task 3A |
| `web_search(query)` | DuckDuckGo analyst commentary search | Agent B · Task 3A |

Tool restriction is enforced at the **schema level** via `llm.bind_tools()` — Agent B cannot call price tools because the schema is never provided to it, not merely instructed not to.

---

## Task 3A — Single Research Agent

- Built with LangGraph `create_react_agent`
- Autonomous tool selection — agent decides order based on observations, no hard-coded sequence
- At least one full **observe → result → decide next action** cycle visible in notebook output
- **Final report structure:** Financial Health Summary · Top Three Risks (with evidence) · Hedge Strategy Recommendation
- Graceful tool failure handling — structured error with `fallback_hint`, agent continues

---

## Task 3B — Multi-Agent Coordination

- **Agent A** (Data Analyst): `get_price_data`, `calculate_volatility`, `llm_sentiment`
- **Agent B** (Research Writer): `web_search`, `get_news`
- Handoff via **Pydantic `DataBrief`** — typed contract validated on construction; raw string passing not used
- **Critique loop:** Agent B sends one specific `clarification_request` back to Agent A → Agent A responds with requested data → Agent B incorporates it and produces `FinalReport`
- Complete agent message trace visible in notebook output (agent speech, tool calls, data handoffs)
- Pipeline runs end-to-end without manual intervention

---

## Task 3C — Memory and Observability

### Short-Term Memory
Agent maintains context across tool calls within a session. A follow-up question is answered from `_session_memory` without re-calling any tool — demonstrated in notebook output.

### Persistent Cache
After a session, the research brief is saved to `research_cache/<TICKER>_<DATE>.json`. On a subsequent run with the same ticker and date, the system detects the cached file and loads it instead of re-running all tools.

### Observability — `agent_trace.jsonl`
Every tool call logs:
```json
{
  "session_id": "...",
  "timestamp": "...",
  "tool_name": "...",
  "inputs": {...},
  "output": "...(truncated to 200 chars)...",
  "duration_ms": 342
}
```
Written **incrementally** — a mid-run crash preserves all prior calls.

---

## Repository Structure

```
task3_agentic/
├── CDAZZDEV_Task3_Agentic_Workflows.ipynb   ← main notebook (run all, outputs visible)
├── dashboard.py                              ← Streamlit observability dashboard
├── README.md
├── logs/
│   └── agent_trace.jsonl                    ← tool call trace (committed to repo)
├── research_cache/
│   └── NVDA_2026-05-11.json                 ← persistent session cache example
└── screenshots/
    ├── dashboard_screenshot.png
    ├── langsmith_trace-1.png
    ├── langsmith_trace-2.png
    └── langsmith_trace-3.png
```

---

## How to Run

### Prerequisites

- **Groq API key** (free) — [console.groq.com](https://console.groq.com)
- **LangSmith API key** (optional, bonus) — [smith.langchain.com](https://smith.langchain.com)
- **ngrok auth token** (optional, for Streamlit tunnel) — [ngrok.com](https://ngrok.com)

### Google Colab

1. Open the notebook via the badge above
2. Add secrets (🔑 sidebar): `GROQ_API_KEY`, `LANGSMITH_API_KEY` (optional), `NGROK_AUTHTOKEN` (optional)
3. **Runtime → Run All** (Cells 1 → 16)

### Change ticker

```python
# Cell 11
TICKER = "NVDA"   # ← change here
```

Re-run Cell 11 with the same ticker and date to demonstrate persistent cache loading.

### Streamlit Dashboard (local)

```bash
pip install streamlit plotly
streamlit run dashboard.py
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| LangGraph `create_react_agent` for Task 3A | Production-grade, maintained observe-reason-act loop; handles tool schema injection automatically |
| Custom `_react_loop()` for Task 3B | Explicit control over critique loop, deterministic handoff assertion, clear interrupt/resume |
| `bind_tools()` for tool restriction | Schema-level enforcement — not a "please don't" prompt instruction |
| Pydantic `DataBrief` as inter-agent contract | Validates handoff on construction; surfaces malformed output immediately |
| Incremental `agent_trace.jsonl` writes | Crash-resilient — every call flushed to disk as it happens |
| Streamlit over LangSmith as primary dashboard | Works without external accounts or API keys; runs in the same Colab instance |

---

## Observability Platform Integration

### Streamlit Dashboard

Reads `agent_trace.jsonl` and displays:
- KPI cards (total calls, total duration, unique tools)
- Tool call timeline
- Duration bar chart per tool
- Tool distribution pie chart
- Session selector and expandable detail rows

```bash
streamlit run dashboard.py
```

![Streamlit Dashboard](screenshots/dashboard_screenshot.png)

### LangSmith

All LangChain calls auto-traced to project `cdazzdev-task3-financial-research` via `LANGCHAIN_TRACING_V2=true` — zero code changes to agents required.

![LangSmith Trace](screenshots/langsmith_trace-1.png)

---

## Tech Stack

| Component | Library / Service |
|-----------|------------------|
| LLM | Groq `llama-3.3-70b-versatile` |
| Agent framework | LangGraph `create_react_agent` · custom ReAct loop |
| Tool restriction | `llm.bind_tools()` |
| Structured output | Pydantic v2 |
| Financial data | yfinance |
| Web search | duckduckgo-search |
| Observability | `agent_trace.jsonl` · LangSmith · Streamlit · Plotly |
| Tunnelling | pyngrok (Colab → Streamlit) |


---

## Known Limitations

- **Groq rate limits** — `time.sleep(2)` added between Task 3A and 3B on free tier
- **yfinance schema variability** — defensive `.get()` chains throughout news parsing
- **DuckDuckGo timeouts** — caught, returns structured `{"error": ..., "fallback_hint": ...}`
- **LLM JSON compliance** — LLaMA-3.3-70b occasionally wraps JSON in markdown fences; triple-backtick stripping applied before `json.loads()`
- **Critique loop detection** — substring check for `"clarification_request"` is brittle; a dedicated classification call would be more robust


---

← [Back to root README](../README.md)