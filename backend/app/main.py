import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import cache, scanner, scheduler
from .config import TOP_N

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="THNDR Scout")

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.on_event("startup")
def on_startup():
    scheduler.start()
    if cache.load() is None:
        scanner.run_scan_in_background()


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


@app.get("/api/status")
def get_status():
    snapshot = cache.load()
    return {
        "is_scanning": scanner.is_scanning,
        "last_updated": snapshot.get("generated_at") if snapshot else None,
        "has_data": snapshot is not None,
    }


@app.get("/api/rankings")
def get_rankings():
    snapshot = cache.load()
    if snapshot is None:
        return {"generated_at": None, "is_scanning": scanner.is_scanning, "results": []}

    results = snapshot["results"][:TOP_N]
    # Trim heavy fields the list view doesn't need.
    trimmed = [{k: v for k, v in row.items() if k != "top_headlines"} for row in results]
    return {
        "generated_at": snapshot["generated_at"],
        "is_scanning": scanner.is_scanning,
        "results": trimmed,
    }


@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    snapshot = cache.load()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No scan data yet")

    for row in snapshot["results"]:
        if row["ticker"].lower() == ticker.lower():
            return row
    raise HTTPException(status_code=404, detail=f"{ticker} not found in latest scan")


@app.post("/api/refresh")
def trigger_refresh():
    if scanner.is_scanning:
        return {"status": "already_scanning"}
    scanner.run_scan_in_background()
    return {"status": "started"}


# Serve the frontend last so /api/* above takes precedence.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
