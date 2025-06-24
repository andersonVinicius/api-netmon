from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import sqlite3
import datetime as dt
from pathlib import Path
import os

from logEntry import LogEntry
from stats import Stats

DB_PATH = os.getenv("DB_PATH", str(Path.home() / "internet_logs" / "connectivity.db"))
app = FastAPI(title="api-monitoramento-rede")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")

@app.get("/logs", response_model=List[LogEntry])
def read_logs(
    limit: int = Query(100, gt=0),
    target: Optional[str] = None,
    method: Optional[str] = Query(None, regex="^(PING|HTTP)$"),
    status: Optional[str] = Query(None, regex="^(OK|FAIL)$"),
    since: Optional[dt.datetime] = None,
    until: Optional[dt.datetime] = None,
):
    conn = get_db_connection()
    # Build base query and parameters
    query = "SELECT * FROM logs"
    clauses = []
    params: list = []
    if target:
        clauses.append("target = ?")
        params.append(target)
    if method:
        clauses.append("method = ?")
        params.append(method)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if since:
        clauses.append("timestamp >= ?")
        params.append(since.isoformat())
    if until:
        clauses.append("timestamp <= ?")
        params.append(until.isoformat())
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    # Execute query and fetch rows
    rows = conn.execute(query, params).fetchall()
    conn.close()
    # Convert rows to LogEntry models
    return [LogEntry(**row) for row in rows]

@app.get("/stats", response_model=Stats)
def get_stats(
    since: Optional[dt.datetime] = None,
    until: Optional[dt.datetime] = None
):
    conn = get_db_connection()
    # Build base query and parameters
    query = "SELECT status, latency_ms FROM logs"
    clauses = []
    params: list = []
    if since:
        clauses.append("timestamp >= ?")
        params.append(since.isoformat())
    if until:
        clauses.append("timestamp <= ?")
        params.append(until.isoformat())
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    # Fetch rows
    rows = conn.execute(query, params).fetchall()
    conn.close()

    # Compute statistics
    total = len(rows)
    success = sum(1 for row in rows if row["status"] == "OK")
    failure = sum(1 for row in rows if row["status"] == "FAIL")
    latencies = [row["latency_ms"] for row in rows if row["status"] == "OK" and row["latency_ms"] is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    return Stats(
        total=total,
        success=success,
        failure=failure,
        avg_latency=avg_latency
    )

@app.get("/", include_in_schema=False)
def root():
    return {"message": "api-monitoramento-rede is running."}