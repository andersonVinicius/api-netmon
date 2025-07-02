from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogModemEntry(BaseModel):
    id: int
    timestamp: datetime  # Ou use datetime se preferir parse automático
    modulo: Optional[str] = None
    nivel: Optional[str] = None
    mensagem: Optional[str] = None