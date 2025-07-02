from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class MonitorQosEntry(BaseModel):
    id: int
    timestamp: datetime
    download: Optional[float] = None
    upload: Optional[float] = None
    latency: Optional[float] = None
    buffer_bloat: Optional[float] = None
    isp: Optional[str] = None
    user_ip: Optional[str] = None
    server_url: Optional[str] = None