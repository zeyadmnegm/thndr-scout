# THNDR Scout

A self-hosted scanner that ranks EGX-listed stocks (the market THNDR trades)
by a mechanical blend of price momentum, valuation, dividend yield,
liquidity, volatility, and free news sentiment — then serves a single-page
dashboard showing the top picks.

**Not financial advice.** Scores are a heuristic, not a recommendation.
Always cross-check tickers against what's actually tradable in your THNDR
app before acting on anything here.

## How it works

- **Prices/fundamentals**: [yfinance](https://github.com/ranaroussi/yfinance)
  pulls free data from Yahoo Finance using EGX's `.CA` ticker suffix
  (e.g. `COMI.CA` = Commercial International Bank).
- **News**: Google News RSS search per company (no API key needed).
- **Sentiment**: a small finance-word lexicon counts positive vs. negative
  terms in recent headlines — simple and free, not an LLM call.
- **Scoring**: each metric is turned into a percentile rank across the
  universe, then combined with the weights in
  [`backend/app/config.py`](backend/app/config.py).
- **Universe**: a curated list of ~30 liquid EGX names in
  [`backend/app/universe.py`](backend/app/universe.py) — edit this file to
  add/remove tickers.
- A background job re-scans automatically every `SCAN_INTERVAL_HOURS`
  (default 6h) as long as the app is running. There's also a manual
  "Rescan now" button in the UI.

## 1. Install Python

Neither Python nor Node is installed on this machine yet. Get Python 3.11+
from [python.org/downloads](https://www.python.org/downloads/) (check
"Add python.exe to PATH" during install), or via winget:

```bash
winget install Python.Python.3.12
```

Restart your terminal afterward so `python`/`pip` are on PATH.

## 2. Set up and run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000**. The first load kicks off a background scan
(takes 1-2 minutes for ~30 tickers); the page polls and updates itself when
it's done.

## Deployment: GitHub Pages + a scheduled scan (free, no card, no server)

The deployed version doesn't run `uvicorn` at all. Instead:

- **[.github/workflows/scan.yml](.github/workflows/scan.yml)** runs
  `backend/scan_once.py` on a schedule (every 6h) via GitHub Actions (free,
  no card required) and commits the result to
  `docs/data/latest_scan.json`.
- **`docs/`** is a static copy of the frontend that fetches that JSON file
  directly instead of calling a live API. GitHub Pages serves it for free
  at `https://<username>.github.io/<repo>/`.

This needs a **public** GitHub repo (Pages on private repos requires a paid
GitHub plan) and, one time, enabling Pages for the repo (Settings → Pages →
Deploy from branch → `main` → `/docs`).

To trigger a scan manually instead of waiting for the schedule: repo →
**Actions** tab → **Scan EGX market** → **Run workflow**.

## Running it live locally instead

`backend/` is still a normal FastAPI app you can run yourself if you want a
live server with on-demand rescans, rather than the static/scheduled setup
above:

```bash
cd backend
uvicorn app.main:app --port 8000
```

Running `uvicorn` in a terminal only scans while that terminal is open —
keep it running in the background with Windows Task Scheduler (run at
login, `pythonw.exe -m uvicorn app.main:app --port 8000`) if you want it
resident on your own machine. This is **not** reachable from outside your
machine unless you additionally expose it (e.g. a tunnel), which has real
security implications for your network — worth doing deliberately, not by
default.

## Tuning

- `backend/app/config.py` — scoring weights, scan interval, how many
  results to show.
- `backend/app/universe.py` — the stock list. This is the main thing worth
  keeping in sync with THNDR's actual catalog since there's no public API
  to pull it automatically.
- `backend/app/analysis/sentiment.py` — the positive/negative word lists,
  if you want sharper sentiment signal.

## Known limitations

- Yahoo Finance data for EGX names can be thin or occasionally stale —
  this is a free, unofficial source, not a licensed data feed.
- News sentiment is keyword counting, not language understanding — it will
  miss sarcasm, negation, and Arabic-language coverage.
- The universe list is manually curated and may not exactly match THNDR's
  live offering.
