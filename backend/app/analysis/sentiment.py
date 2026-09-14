"""
Lightweight lexicon-based sentiment scoring for financial news headlines.

This is deliberately simple (no LLM call, no external sentiment API) so the
whole tool runs on free infrastructure. It counts finance-relevant positive
and negative words per headline/summary and nets them out. It is a rough
signal, not a substitute for actually reading the news.
"""

import re

POSITIVE_WORDS = {
    "surge", "surges", "surged", "growth", "grows", "grew", "profit", "profits",
    "beat", "beats", "upgrade", "upgraded", "expansion", "expands", "record",
    "strong", "gain", "gains", "rally", "rallies", "buy", "outperform", "boost",
    "boosts", "rise", "rises", "rising", "jump", "jumps", "soar", "soars",
    "recovery", "recovers", "positive", "improve", "improves", "improved",
    "invest", "investment", "investments", "dividend", "dividends", "high",
    "higher", "success", "successful", "win", "wins", "award", "partnership",
    "acquire", "acquisition", "milestone",
}

NEGATIVE_WORDS = {
    "loss", "losses", "decline", "declines", "declined", "drop", "drops",
    "dropped", "downgrade", "downgraded", "lawsuit", "fraud", "crisis",
    "plunge", "plunges", "sell-off", "selloff", "weak", "weaker", "cut",
    "cuts", "risk", "risks", "default", "delay", "delays", "delayed", "fine",
    "fined", "probe", "investigation", "fall", "falls", "falling", "slump",
    "slumps", "warning", "warns", "layoff", "layoffs", "strike", "shortage",
    "debt", "inflation", "recession", "bankruptcy", "scandal", "suspend",
    "suspended", "resign", "resigns", "resignation",
}

_WORD_RE = re.compile(r"[a-zA-Z]+")


def score_articles(articles: list[dict]) -> dict:
    """
    Returns {score: -100..100, article_count, positive_hits, negative_hits}.
    score is 0 (neutral) when there isn't enough text to judge either way.
    """
    positive_hits = 0
    negative_hits = 0

    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        words = _WORD_RE.findall(text)
        positive_hits += sum(1 for w in words if w in POSITIVE_WORDS)
        negative_hits += sum(1 for w in words if w in NEGATIVE_WORDS)

    total = positive_hits + negative_hits
    score = ((positive_hits - negative_hits) / total * 100) if total else 0.0

    return {
        "score": score,
        "article_count": len(articles),
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
    }
