# REFLECTION.md

## Architectural Decisions

**Why Pydantic over raw JSON validation?**
Pydantic provides automatic type coercion, field-level validation with custom validators,
and clear error messages that tell you exactly which field failed and why. This makes
debugging LLM output failures much faster than manually checking JSON dicts.

**Why Groq Llama-3.3-70b-versatile?**
Groq provides extremely low-latency inference (typically under 1s for 700 tokens) compared
to other free options. The 70B parameter model produces more nuanced financial reasoning
than smaller models, which is critical for the signal justification quality.

**Why AAPL as the ticker?**
Apple has dense news coverage, well-populated yfinance data, and consistent P/E ratio
reporting — reducing the risk of null values that could break the pipeline.

**Why Wilder's smoothing for RSI?**
The original RSI formula defined by J. Welles Wilder (1978) uses his smoothing method
which is an EWM with alpha=1/period and adjust=False. Most charting platforms use this
definition, so our values align with industry tools for comparability.

## What I Would Improve With More Time

1. **Streaming LLM responses** — for longer analysis, streaming would improve user experience
2. **News source diversity** — add Alpha Vantage news API as a second source for better coverage
3. **Backtesting module** — validate the momentum signal against historical price movements
4. **Caching layer** — cache OHLCV data locally to avoid repeated API calls during development
5. **More indicators** — add Average True Range (ATR) for volatility context

## Limitations Encountered

1. **yfinance news endpoint** — sometimes returns fewer than 10 headlines for less-covered tickers;
   mitigated with the GNews RSS fallback
2. **P/E ratio availability** — `info.get('trailingPE')` returns None for some tickers;
   handled with `safe_float()` and graceful fallback
3. **Groq rate limits** — free tier has rate limits; mitigated with exponential backoff retry logic
4. **SMA-200 warmup** — needs 200+ trading days of data; first 200 rows have NaN SMA-200,
   which is expected and documented in the notebook output