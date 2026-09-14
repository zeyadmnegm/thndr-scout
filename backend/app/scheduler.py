"""Background job that keeps the scan fresh without any manual trigger."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from .config import SCAN_INTERVAL_HOURS
from .scanner import run_scan

log = logging.getLogger("thndr_scout.scheduler")

_scheduler = BackgroundScheduler()


def start() -> None:
    _scheduler.add_job(
        run_scan,
        "interval",
        hours=SCAN_INTERVAL_HOURS,
        id="market_scan",
        next_run_time=None,  # first run is kicked off explicitly at startup
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    log.info("Scheduler started: rescanning every %d hours", SCAN_INTERVAL_HOURS)


def shutdown() -> None:
    _scheduler.shutdown(wait=False)
