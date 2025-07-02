from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import sqlite3
import datetime as dt
from pathlib import Path
import os

from logEntry import LogEntry
from stats import Stats
from monitorQosEntry import MonitorQosEntry
from logModemEntry import LogModemEntry

DB_PATH = os.getenv("DB_PATH", str(Path.home() / "internet_logs" / "connectivity.db"))
app = FastAPI(
    title="API Monitoramento de Rede",
    description="API para monitoramento de rede, logs do modem e análise de QoS.",
    version="1.1.0"
)

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")

@app.get("/logs", response_model=List[LogEntry],
         tags=["Logs"],
         summary="Consultar logs de monitoramento",
         description="Retorna logs gerais, permite filtrar por destino, método, status e intervalo de datas.")
def read_logs(
    limit: int = Query(100, gt=0, description="Quantidade máxima de logs a retornar."),
    target: Optional[str] = Query(None, description="Destino (IP ou hostname)."),
    method: Optional[str] = Query(None, pattern="^(PING|HTTP)$", description="Método de monitoramento: PING ou HTTP."),
    status: Optional[str] = Query(None, pattern="^(OK|FAIL)$", description="Status do teste: OK ou FAIL."),
    since: Optional[dt.datetime] = Query(None, description="Data inicial (ISO 8601) para filtro."),
    until: Optional[dt.datetime] = Query(None, description="Data final (ISO 8601) para filtro.")
):
    conn = get_db_connection()
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
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [LogEntry(**row) for row in rows]

@app.get("/stats", response_model=Stats,
         tags=["Estatísticas"],
         summary="Obter estatísticas dos logs",
         description="Retorna estatísticas de sucesso, falha e média de latência, com filtros opcionais por data.")
def get_stats(
    since: Optional[dt.datetime] = Query(None, description="Data inicial para filtro."),
    until: Optional[dt.datetime] = Query(None, description="Data final para filtro.")
):
    conn = get_db_connection()
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
    rows = conn.execute(query, params).fetchall()
    conn.close()

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

@app.get("/monitor_qos", response_model=List[MonitorQosEntry],
         tags=["QoS"],
         summary="Consultar resultados de análise QoS",
         description="Retorna resultados do monitoramento de qualidade de serviço (QoS). Permite filtrar por data.")
def read_monitor_qos(
    limit: int = Query(100, gt=0, description="Quantidade máxima de resultados."),
    since: Optional[dt.datetime] = Query(None, description="Data inicial para filtro."),
    until: Optional[dt.datetime] = Query(None, description="Data final para filtro.")
):
    conn = get_db_connection()
    query = "SELECT * FROM analise_qos"
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
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [MonitorQosEntry(**row) for row in rows]

@app.get("/logs_modem", response_model=List[LogModemEntry],
         tags=["Logs Modem"],
         summary="Consultar logs do modem",
         description="Consulta registros de logs coletados diretamente do modem. Filtros por módulo, nível, mensagem e datas disponíveis.")
def read_logs_modem(
    limit: int = Query(100, gt=0, description="Quantidade máxima de registros."),
    modulo: Optional[str] = Query(None, description="Módulo (ex: PPPoE, DHCP, etc)."),
    nivel: Optional[str] = Query(None, description="Nível do log (INFO, ERROR, etc)."),
    mensagem: Optional[str] = Query(None, description="Filtrar por trecho da mensagem (busca parcial)."),
    since: Optional[dt.datetime] = Query(None, description="Data inicial (ISO 8601) para filtro."),
    until: Optional[dt.datetime] = Query(None, description="Data final (ISO 8601) para filtro.")
):
    conn = get_db_connection()
    query = "SELECT * FROM logs_modem"
    clauses = []
    params: list = []
    if modulo:
        clauses.append("modulo = ?")
        params.append(modulo)
    if nivel:
        clauses.append("nivel = ?")
        params.append(nivel)
    if mensagem:
        clauses.append("mensagem LIKE ?")
        params.append(f"%{mensagem}%")
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
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [LogModemEntry(**row) for row in rows]

@app.get("/", include_in_schema=False)
def root():
    return {"message": "api-monitoramento-rede is running."}