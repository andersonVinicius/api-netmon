import time
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


DEFAULT_DB = Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "data" / "connectivity.db")))
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

class FastSpeedTest:
    def __init__(self, headless=True):
        self.headless = headless
        self.url = "https://fast.com/pt/#"
        self.driver = None

    def start_driver(self):
        options = Options()
        options.binary_location = "/usr/bin/chromium"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/chromedriver")  # caminho explícito do driver

        self.driver = webdriver.Chrome(service=service, options=options)
    def wait_for_final_value(self, element_id, interval=1, stable_checks=5):
        last_value = None
        stable_count = 0
        while True:
            value = self.driver.find_element(By.ID, element_id).text
            if value == last_value and value not in ["0", ""]:
                stable_count += 1
            else:
                stable_count = 0
            if stable_count >= stable_checks:
                return value
            last_value = value
            time.sleep(interval)

    def run_test(self):
        self.start_driver()
        try:
            self.driver.get(self.url)
            print("Página carregada, aguardando resultado final...")
            download = float(self.wait_for_final_value("speed-value"))
            download_units = self.driver.find_element(By.ID, "speed-units").text
            # Clica no botão "Mostrar mais informações"
            btn_info = self.driver.find_element(By.ID, "show-more-details-link")
            btn_info.click()
            time.sleep(1)
            upload = float(self.wait_for_final_value("upload-value"))
            upload_units = self.driver.find_element(By.ID, "upload-units").text
            latency_unloaded = float(self.driver.find_element(By.ID, "latency-value").text)
            latency_loaded = float(self.driver.find_element(By.ID, "bufferbloat-value").text)
            # Converte unidades se necessário
            if "Gbps" in download_units:
                download *= 1000
            if "Gbps" in upload_units:
                upload *= 1000
            return download, upload, latency_unloaded, latency_loaded
        except Exception as e:
            print("Erro (provavelmente sem internet):", e)
            # Retorna valores padronizados
            return 0, 0, 0, 0
        finally:
            self.close()

    def close(self):
        if self.driver is not None:
            self.driver.quit()

def criar_tabela():
    con = sqlite3.connect(DEFAULT_DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analise_qos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download REAL,
            upload REAL,
            latency_unloaded REAL,
            latency_loaded REAL
        )
    """)
    con.commit()
    con.close()

def salvar_sqlite(download, upload, latency_unloaded, latency_loaded):
    ts = datetime.now().astimezone().isoformat()
    con = sqlite3.connect(DEFAULT_DB)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO analise_qos (timestamp, download, upload, latency_unloaded, latency_loaded) VALUES (?, ?, ?, ?, ?)",
        (ts, download, upload, latency_unloaded, latency_loaded)
    )
    con.commit()
    con.close()

if __name__ == "__main__":
    criar_tabela()
    while True:
        test = FastSpeedTest(headless=True)
        download, upload, latency_unloaded, latency_loaded = test.run_test()
        print("Salvando: ", download, upload, latency_unloaded, latency_loaded)
        salvar_sqlite(download, upload, latency_unloaded, latency_loaded)
        print("Aguardando 30 segundos para próximo teste...\n")
        time.sleep(30)

# #!/usr/bin/env python3
# import subprocess
# import json
# import time
# import sqlite3
# from datetime import datetime
# from pathlib import Path
#
# import pytz
# import os
#
# DEFAULT_DB = Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "data" / "connectivity.db")))
# DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
#
# def init_db():
#     con = sqlite3.connect(DEFAULT_DB)
#     cur = con.cursor()
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS analise_qos (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             download_mbps REAL,
#             latency_ms REAL,
#             buffer_bloat REAL,
#             user_location TEXT,
#             client_ip TEXT
#         )
#     """)
#     con.commit()
#     con.close()
#
# def run_fast_test():
#     try:
#         proc = subprocess.run(
#             ["fast", "--json"],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         print("Pronto pra ler o processs")
#         data = json.loads(proc.stdout)
#         print("Data:", data)
#         return {
#             "download_mbps": data.get("downloadSpeed"),
#             "latency_ms": data.get("latency"),
#             "buffer_bloat": data.get("bufferBloat"),
#             "user_location": data.get("userLocation"),
#             "client_ip": data.get("userIp"),
#         }
#     except Exception:
#         # Em caso de erro, retorna campos nulos/zero conforme pedido
#         return {
#             "download_mbps": None,
#             "latency_ms": None,
#             "buffer_bloat": None,
#             "user_location": None,
#             "client_ip": None,
#         }
#
# def save_to_db(res):
#     tz = pytz.timezone("America/Sao_Paulo")
#     timestamp = datetime.now(tz).isoformat()
#
#     con = sqlite3.connect(DEFAULT_DB)
#     cur = con.cursor()
#     cur.execute("""
#         INSERT INTO analise_qos (
#             timestamp, download_mbps,
#             latency_ms, buffer_bloat, user_location, client_ip
#         ) VALUES (?, ?, ?, ?, ?, ?)
#     """, (
#         timestamp,
#         res.get("download_mbps"),
#         res.get("latency_ms"),
#         res.get("buffer_bloat"),
#         res.get("user_location"),
#         res.get("client_ip"),
#     ))
#     con.commit()
#     con.close()
#
# if __name__ == "__main__":
#     init_db()
#     print("Start monitor qos")
#     while True:
#         result = run_fast_test()
#         save_to_db(result)
#         print("Log salvo:", result)
#         time.sleep(30)  # Troque para 3600 para rodar de hora em hora se quiser