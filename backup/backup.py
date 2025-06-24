#!/usr/bin/env python3
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Usa a variável de ambiente DB_PATH (o mesmo do Compose)
DB = Path(os.getenv("DB_PATH", "/data/connectivity.db"))
BACKUP_DIR = DB.parent / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MAX_BACKUPS = 3

def backup_db():
    if not DB.exists():
        print("Arquivo de banco não encontrado.")
        return

    ts = datetime.now(timezone.utc).strftime("connectivity_%Y%m%dT%H%M%SZ.db")
    dest = BACKUP_DIR / ts
    shutil.copy2(DB, dest)
    print(f"Backup criado: {dest}")

    files = sorted(BACKUP_DIR.glob("connectivity_*.db"), reverse=True)
    for old in files[MAX_BACKUPS:]:
        old.unlink()
        print(f"Removido backup antigo: {old}")

if __name__ == "__main__":
    backup_db()