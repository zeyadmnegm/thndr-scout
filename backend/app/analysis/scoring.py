"""Combines price, fundamentals and news sentiment into one ranked list."""

from ..config import PE_MAX, PE_MIN, WEIGHTS

_FACTOR_LABELS = {
    "momentum_3m": "strong 3-month momentum ({momentum_3m:+.1f}%)",
    "momentum_1m": "solid recent momentum ({momentum_1m:+.1f}%)",
    "valuation": "attractive valuation (P/E {trailing_pe:.1f})",
    "dividend_yield": "a high dividend yield ({dividend_yield:.1f}%)",
    "liquidity": "strong trading liquidity",
    "low_volatility": "low price volatility",
    "sentiment": "positive recent news ({article_count} articles)",
}


def _percentile_ranks(values: dict[str, float]) -> dict[str, float]:
    """
    Maps each key to its percentile (0-100) among the given values.

    Equal values get the same (averaged) percentile rather than being spread
    out by insertion order — otherwise a block of tickers all tied at, say,
    0% dividend yield would get arbitrarily stretched across the whole 0-80%
    range just because of how they happened to sort, making some of them
    look meaningfully better than others when they're identical.
    """
    if not values:
        return {}
    ordered = sorted(values.items(), key=lambda kv: kv[1])
    n = len(ordered)
    ranks: dict[str, float] = {}
    i = 0
    while i < n:
        j = i
        while j < n and ordered[j][1] == ordered[i][1]:
            j += 1
        avg_index = (i + j - 1) / 2
        pct = 100.0 * avg_index / (n - 1) if n > 1 else 50.0
        for k in range(i, j):
            ranks[ordered[k][0]] = pct
        i = j
    return ranks


def rank_universe(rows: list[dict]) -> list[dict]:
    """
    `rows` is one dict per ticker merging universe metadata, price metrics,
    fundamentals and sentiment. Returns the same rows sorted best-first, each
    annotated with `score` (0-100) and a one-line `blurb`.
    """
    valid_pe = {
        r["ticker"]: r["trailing_pe"]
        for r in rows
        if r.get("trailing_pe") and PE_MIN < r["trailing_pe"] < PE_MAX
    }
    # Lower P/E is "better" for this simple heuristic, so rank inverted P/E.
    pe_ranks = _percentile_ranks({t: -pe for t, pe in valid_pe.items()})

    momentum_3m_ranks = _percentile_ranks({r["ticker"]: r.get("momentum_3m", 0.0) for r in rows})
    momentum_1m_ranks = _percentile_ranks({r["ticker"]: r.get("momentum_1m", 0.0) for r in rows})
    dividend_ranks = _percentile_ranks({r["ticker"]: r.get("dividend_yield", 0.0) for r in rows})
    liquidity_ranks = _percentile_ranks({r["ticker"]: r.get("avg_volume", 0.0) for r in rows})
    volatility_ranks = _percentile_ranks({r["ticker"]: -r.get("volatility", 0.0) for r in rows})
    sentiment_ranks = _percentile_ranks({r["ticker"]: r.get("sentiment_score", 0.0) for r in rows})

    for row in rows:
        ticker = row["ticker"]
        factor_scores = {
            "momentum_3m": momentum_3m_ranks.get(ticker, 50.0),
            "momentum_1m": momentum_1m_ranks.get(ticker, 50.0),
            "valuation": pe_ranks.get(ticker, 50.0),
            "dividend_yield": dividend_ranks.get(ticker, 50.0),
            "liquidity": liquidity_ranks.get(ticker, 50.0),
            "low_volatility": volatility_ranks.get(ticker, 50.0),
            "sentiment": sentiment_ranks.get(ticker, 50.0),
        }
        row["score"] = round(sum(factor_scores[f] * w for f, w in WEIGHTS.items()), 1)
        row["blurb"] = _build_blurb(row, factor_scores)

    return sorted(rows, key=lambda r: r["score"], reverse=True)


def _factor_is_meaningful(factor: str, row: dict) -> bool:
    """
    A factor can win a high percentile purely by tying with a large block of
    other tickers at a "no data" baseline (0% yield, 0 articles). Only cite
    it in the blurb when the underlying value actually backs up the claim.
    """
    if factor == "dividend_yield":
        return row.get("dividend_yield", 0.0) > 0.5
    if factor == "sentiment":
        return row.get("article_count", 0) > 0 and row.get("sentiment_score", 0.0) > 10
    if factor == "valuation":
        return row.get("trailing_pe") is not None
    return True


def _build_blurb(row: dict, factor_scores: dict[str, float]) -> str:
    ranked_factors = sorted(factor_scores.items(), key=lambda kv: kv[1], reverse=True)
    phrases = []
    for factor, value in ranked_factors:
        if value < 55 or not _factor_is_meaningful(factor, row):
            continue
        template = _FACTOR_LABELS[factor]
        try:
            phrases.append(template.format(**row))
        except (KeyError, ValueError, TypeError):
            phrases.append(template.split(" (")[0])
        if len(phrases) == 2:
            break

    if not phrases:
        return "No single standout factor; ranks mid-pack across the board."
    return "Ranks high on " + " and ".join(phrases) + "."
