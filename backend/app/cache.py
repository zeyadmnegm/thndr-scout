"""Tiny JSON-file cache for the latest scan result. No database needed."""

import json
import threading
from pathlib import Path

from .config import CACHE_FILE

_lock = threading.Lock()
_path = Path(__file__).resolve().parent.parent / CACHE_FILE


def save(snapshot: dict) -> None:
    _path.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        _path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


def load() -> dict | None:
    with _lock:
        if not _path.exists():
            return None
        return json.loads(_path.read_text(encoding="utf-8"))
