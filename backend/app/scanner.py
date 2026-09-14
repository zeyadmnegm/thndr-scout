"""Orchestrates one full market scan: prices -> fundamentals -> news -> score."""

import logging
import threading
from datetime import datetime, timezone

from . import cache
from .analysis.scoring import rank_universe
from .analysis.sentiment import score_articles
from .data.news import fetch_company_news
from .data.prices import fetch_fundamentals, fetch_price_metrics
from .universe import UNIVERSE

log = logging.getLogger("thndr_scout.scanner")

_scan_lock = threading.Lock()
is_scanning = False


def run_scan() -> dict:
    """Runs synchronously; safe to call from a background thread or job."""
    global is_scanning
    if not _scan_lock.acquire(blocking=False):
        log.info("Scan already in progress, skipping duplicate trigger")
        return cache.load() or {}

    try:
        is_scanning = True
        tickers = [row["ticker"] for row in UNIVERSE]
        log.info("Scanning %d tickers", len(tickers))

        price_metrics = fetch_price_metrics(tickers)
        fundamentals = fetch_fundamentals(tickers)

        rows = []
        for meta in UNIVERSE:
            ticker = meta["ticker"]
            prices = price_metrics.get(ticker)
            if not prices:
                continue  # no usable price history, drop from this scan

            fund = fundamentals.get(ticker, {})
            articles = fetch_company_news(meta["name"])
            sentiment = score_articles(articles)

            rows.append(
                {
                    **meta,
                    **prices,
                    "trailing_pe": fund.get("trailing_pe"),
                    "dividend_yield": fund.get("dividend_yield", 0.0),
                    "sentiment_score": sentiment["score"],
                    "article_count": sentiment["article_count"],
                    "top_headlines": [a["title"] for a in articles[:5]],
                }
            )

        ranked = rank_universe(rows)
        snapshot = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "results": ranked,
        }
        cache.save(snapshot)
        log.info("Scan complete: %d tickers ranked", len(ranked))
        return snapshot
    finally:
        is_scanning = False
        _scan_lock.release()


def run_scan_in_background() -> None:
    threading.Thread(target=run_scan, daemon=True).start()
