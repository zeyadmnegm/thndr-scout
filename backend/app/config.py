"""Central knobs for the scanner. Edit here, not in the analysis code."""

# How often the background scheduler re-scans the market.
SCAN_INTERVAL_HOURS = 6

# How many top-ranked names the frontend shows.
TOP_N = 12

# How many days of news to pull per company.
NEWS_LOOKBACK_DAYS = 14

# Composite score weights. Must sum to 1.0.
WEIGHTS = {
    "momentum_3m": 0.25,
    "momentum_1m": 0.10,
    "valuation": 0.15,
    "dividend_yield": 0.15,
    "liquidity": 0.10,
    "low_volatility": 0.10,
    "sentiment": 0.15,
}

# Reasonable bounds for a valid trailing P/E on EGX names; outside this range
# (or missing) is treated as "unknown" rather than good or bad.
PE_MIN, PE_MAX = 0, 60

CACHE_FILE = "data/latest_scan.json"
