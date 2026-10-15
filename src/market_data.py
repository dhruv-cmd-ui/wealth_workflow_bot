"""Fetches a free, no-API-key market snapshot (Nifty 50 / Sensex) via yfinance.

Degrades gracefully: any failure returns None so the caller can fall back to
a generic templated post instead of crashing the scheduled run.
"""


def fetch_market_recap() -> dict | None:
    try:
        import yfinance as yf
    except Exception:
        return None

    tickers = {"Nifty 50": "^NSEI", "Sensex": "^BSESN"}
    result = {}
    try:
        for label, symbol in tickers.items():
            hist = yf.Ticker(symbol).history(period="5d")
            if hist is None or len(hist) < 2:
                return None
            last_close = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            change_pct = (last_close - prev_close) / prev_close * 100
            result[label] = {
                "close": round(last_close, 2),
                "change_pct": round(change_pct, 2),
            }
        return result
    except Exception:
        return None
