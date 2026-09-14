"""
Free news via Google News RSS search (no API key required).

Google News RSS supports arbitrary search queries and returns recent
articles from across the web, which is a reasonable free substitute for a
paid news API for a small personal tool like this.
"""

import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser

from ..config import NEWS_LOOKBACK_DAYS

log = logging.getLogger("thndr_scout.news")

_FEED_URL = "https://news.google.com/rss/search?q={query}&hl=en-EG&gl=EG&ceid=EG:en"


def fetch_company_news(company_name: str, max_items: int = 15) -> list[dict]:
    """Returns recent [{title, summary, published, link}] for a company."""
    query = quote_plus(f'"{company_name}" Egypt stock OR shares OR EGX')
    url = _FEED_URL.format(query=query)

    try:
        feed = feedparser.parse(url)
    except Exception:
        log.warning("News fetch failed for %s", company_name, exc_info=True)
        return []

    # Google ranks entries by relevance, not recency, so filter by date across
    # the whole result set before truncating - otherwise a handful of
    # highly-relevant-but-old items can crowd out genuinely recent news.
    cutoff = datetime.now(timezone.utc) - timedelta(days=NEWS_LOOKBACK_DAYS)
    items = []
    for entry in feed.entries:
        published = _parse_date(entry)
        if published and published < cutoff:
            continue
        items.append(
            {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "published": published.isoformat() if published else None,
                "link": entry.get("link", ""),
            }
        )

    items.sort(key=lambda a: a["published"] or "", reverse=True)
    return items[:max_items]


def _parse_date(entry) -> datetime | None:
    parsed = entry.get("published_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)
