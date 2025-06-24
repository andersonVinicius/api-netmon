from typing import Optional

from pydantic import BaseModel

class Stats(BaseModel):
    total: int
    success: int
    failure: int
    avg_latency: Optional[float]