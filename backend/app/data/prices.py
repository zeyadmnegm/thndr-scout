"""Free market data via Yahoo Finance (yfinance). No API key required."""

import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf

log = logging.getLogger("thndr_scout.prices")


def fetch_price_metrics(tickers: list[str]) -> dict[str, dict]:
    """
    Batch-downloads ~6 months of daily history for all tickers in one request
    and derives momentum / volatility / liquidity from it.

    Returns {ticker: {price, momentum_1m, momentum_3m, volatility, avg_volume}}
    for tickers where enough history was available; missing/broken tickers are
    silently omitted (logged) so one bad symbol doesn't kill the whole scan.
    """
    results: dict[str, dict] = {}
    try:
        data = yf.download(
            tickers,
            period="6mo",
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False,
            auto_adjust=True,
        )
    except Exception:
        log.exception("Bulk price download failed")
        return results

    for ticker in tickers:
        try:
            frame = data[ticker] if len(tickers) > 1 else data
            closes = frame["Close"].dropna()
            volumes = frame["Volume"].dropna()
            if len(closes) < 25:
                continue

            last_price = float(closes.iloc[-1])
            price_1m = float(closes.iloc[-21]) if len(closes) >= 21 else float(closes.iloc[0])
            price_3m = float(closes.iloc[-63]) if len(closes) >= 63 else float(closes.iloc[0])

            daily_returns = closes.pct_change().dropna()

            results[ticker] = {
                "price": last_price,
                "momentum_1m": (last_price / price_1m - 1) * 100 if price_1m else 0.0,
                "momentum_3m": (last_price / price_3m - 1) * 100 if price_3m else 0.0,
                "volatility": float(daily_returns.std() * (252 ** 0.5) * 100) if len(daily_returns) > 1 else 0.0,
                "avg_volume": float(volumes.tail(30).mean()) if len(volumes) else 0.0,
            }
        except Exception:
            log.warning("Skipping %s: could not derive price metrics", ticker, exc_info=True)

    return results


def fetch_fundamentals(tickers: list[str]) -> dict[str, dict]:
    """
    Per-ticker fundamentals (trailing P/E, dividend yield) via yfinance's
    `.info`, which Yahoo doesn't offer in bulk. Fetched concurrently since
    each call is a separate slow network round-trip; failures degrade to
    "unknown" rather than aborting the scan.
    """
    results: dict[str, dict] = {}

    def _one(ticker: str):
        # Yahoo's quoteSummary endpoint rate-limits hard under concurrency
        # (returns an empty/non-JSON body, not a clean HTTP error), so each
        # worker staggers itself and retries a couple of times before giving up.
        for attempt in range(3):
            time.sleep(random.uniform(0.2, 0.6))
            try:
                info = yf.Ticker(ticker).get_info()
                if info:
                    # Yahoo's `dividendYield` field is frequently absent for
                    # foreign (e.g. EGX) listings; `trailingAnnualDividendYield`
                    # is populated far more often for these, so prefer it.
                    yield_fraction = info.get("trailingAnnualDividendYield")
                    if yield_fraction is None:
                        yield_fraction = info.get("dividendYield")
                    return ticker, {
                        "trailing_pe": info.get("trailingPE"),
                        "dividend_yield": (yield_fraction or 0.0) * 100,
                    }
            except Exception:
                pass
            time.sleep(1.0 + attempt)

        log.warning("No fundamentals for %s after retries", ticker)
        return ticker, {"trailing_pe": None, "dividend_yield": 0.0}

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(_one, t) for t in tickers]
        for future in as_completed(futures):
            ticker, values = future.result()
            results[ticker] = values

    return results
