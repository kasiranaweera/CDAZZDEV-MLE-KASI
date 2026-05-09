# Task 1 — Financial AI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](YOUR_COLAB_LINK_HERE)

## What this notebook does
- Fetches 2 years of AAPL OHLCV data via yfinance
- Computes SMA-50, SMA-200, RSI-14, MACD(12,26,9), Bollinger Bands(20,2σ) from scratch
- Retrieves 15 recent news headlines
- Analyses sentiment per headline using Groq Llama-3.3-70b
- Generates a Buy/Hold/Sell signal with Pydantic-validated structured output
- Produces a styled HTML equity research brief with embedded chart