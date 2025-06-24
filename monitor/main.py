#!/usr/bin/env python3
"""
internet_monitor.py – Connectivity logger with SQLite for Orange Pi / Docker
==========================================================================

Features
--------
* **Ping** hosts and/or **HTTP(S)** GET to URLs at a fixed interval.
* Store results in a **SQLite** database (default: `~/internet_logs/connectivity.db`).
* Rotate automatically to a new table each day (optional).
* Optional summary lines to **stdout/syslog**.
* Suitable for running as a **systemd service** or inside **Docker**.

Quick start (bare‑metal)
-----------------------
```bash
python3 internet_monitor.py                # default 30‑second interval
python3 internet_monitor.py -i 10 -t 8.8.8.8 1.1.1.1 \
    --http https://www.google.com https://cloudflare.com
```

Docker usage
------------
1. Build image:
   ```bash
   docker build -t internet-monitor .
   ```
2. Run (persisting DB to host):
   ```bash
   docker run -d --name netmon \
     -v $(pwd)/data:/data \
     internet-monitor -i 30 --syslog
   ```

Environment variables (optional)
--------------------------------
* `DB_PATH` – override default database location.

"""
from __future__ import annotations

import os
from pathlib import Path
print("DB path:", os.getenv("DB_PATH", Path.home() / "internet_logs" / "connectivity.db"))

import argparse
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # HTTP checks disabled if not installed

DEFAULT_DB = Path(os.getenv("DB_PATH", str(Path.home() / "internet_logs" / "connectivity.db")))
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT    NOT NULL,
    target       TEXT    NOT NULL,
    method       TEXT    NOT NULL,
    latency_ms   REAL,
    status       TEXT    NOT NULL
);
"""

INSERT_SQL = (
    "INSERT INTO logs (timestamp, target, method, latency_ms, status) "
    "VALUES (?, ?, ?, ?, ?);"
)


def ensure_schema(conn: sqlite3.Connection):
    conn.execute(SCHEMA_SQL)
    conn.commit()


def ping(host: str, timeout: int = 3) -> Optional[float]:
    """Return latency in ms or None if unreachable."""
    try:
        start = time.perf_counter()
        completed = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if completed.returncode == 0:
            return (time.perf_counter() - start) * 1000.0
    except Exception:
        pass
    return None


def http_get(url: str, timeout: int = 5) -> Optional[float]:
    if requests is None:
        return None
    try:
        start = time.perf_counter()
        r = requests.get(url, timeout=timeout)
        if r.ok:
            return (time.perf_counter() - start) * 1000.0
    except Exception:
        pass
    return None


def log_row(
    conn: sqlite3.Connection,
    target: str,
    method: str,
    latency: Optional[float],
):
    now_brasilia = datetime.now(ZoneInfo("America/Belem"))
    timestamp = now_brasilia.isoformat()
    status = "OK" if latency is not None else "FAIL"

    conn.execute(INSERT_SQL, (timestamp, target, method, latency, status))
    conn.commit()


def monitor(
    interval: int,
    ping_targets: Iterable[str],
    http_targets: Iterable[str],
    use_syslog: bool,
    db_path: Path,
):
    import logging

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    conn = sqlite3.connect(db_path)
    ensure_schema(conn)

    try:
        while True:
            # Ping tests
            for host in ping_targets:
                latency = ping(host)
                log_row(conn, host, "PING", latency)
                if use_syslog:
                    logging.info("PING %s %s %.2f ms", host, "OK" if latency else "FAIL", latency or 0)

            # HTTP tests
            for url in http_targets:
                latency = http_get(url)
                log_row(conn, url, "HTTP", latency)
                if use_syslog:
                    logging.info("HTTP %s %s %.2f ms", url, "OK" if latency else "FAIL", latency or 0)

            time.sleep(interval)
    finally:
        conn.close()


def parse_args(argv: Sequence[str]):
    p = argparse.ArgumentParser(description="Internet connectivity monitor with SQLite logging")
    p.add_argument("-i", "--interval", type=int, default=30, help="Interval between checks in seconds (≥5)")
    p.add_argument("-t", "--targets", nargs="*", default=[], help="Hosts to ping")
    p.add_argument("--http", nargs="*", default=[], help="HTTP/HTTPS URLs to fetch")
    p.add_argument("--syslog", action="store_true", help="Log summary lines to stdout/syslog")
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path (default: %(default)s)")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    monitor(
        interval=max(5, args.interval),
        ping_targets=args.targets,
        http_targets=args.http,
        use_syslog=args.syslog,
        db_path=args.db,
    )
