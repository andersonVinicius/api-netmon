from typing import Optional

from pydantic import BaseModel
import datetime as dt

class LogEntry(BaseModel):
    id: int
    timestamp: dt.datetime
    target: str
    method: str
    latency_ms: Optional[float]
    status: str