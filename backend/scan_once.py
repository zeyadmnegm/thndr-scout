"""
Runs a single market scan and writes the result as a static JSON file that
the GitHub Pages frontend (docs/) fetches directly - no live server needed.
Invoked on a schedule by .github/workflows/scan.yml.
"""

import json
from pathlib import Path

from app.scanner import run_scan


def main():
    snapshot = run_scan()
    docs_path = Path(__file__).resolve().parent.parent / "docs" / "data" / "latest_scan.json"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {len(snapshot.get('results', []))} results to {docs_path}")


if __name__ == "__main__":
    main()
