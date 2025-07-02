import sqlite3
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import pytz
import os

# Configuração do banco de dados
# db_dir = "data"
# db_path = os.path.join(db_dir, "connectivity.db")
# os.makedirs(db_dir, exist_ok=True)

DEFAULT_DB = Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "data" / "connectivity.db")))
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
# print(db_dir)
# DB_PATH = Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "data" / "connectivity.db")))
# DB_PATH.parent.mkdir(DB_PATH, exist_ok=True)

# Função para converter a data/hora do log para ISO 8601
def parse_data_hora(data_hora_str):
    # Exemplo de entrada: "27.06.2025 - 18:08:13"
    dt = datetime.strptime(data_hora_str, "%d.%m.%Y - %H:%M:%S")
    tz = pytz.timezone("America/Belem")  # Ajuste para o seu fuso se necessário
    dt = tz.localize(dt)
    return dt.isoformat()  # Exemplo: '2025-06-26T18:06:46.370195-03:00'

def salvar_logs():
    # Configuração do Selenium
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")  # caminho explícito do driver

    driver = webdriver.Chrome(service=service, options=options)

    # from selenium import webdriver
    # from selenium.webdriver.chrome.options import Options
    #
    # options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    #
    # driver = webdriver.Chrome(options=options)


    try:
        # 1. Login
        driver.get("http://192.168.0.1/2.0/gui/login")
        time.sleep(2)
        usuario = os.getenv("MODEM_USER")
        senha = os.getenv("MODEM_PASS")
        if not usuario or not senha:
            raise RuntimeError("As variáveis de ambiente MODEM_USER e MODEM_PASS não estão definidas! Adicione o arquivo .env")
        campo_usuario = driver.find_element(By.XPATH, '//input[@type="text" or @name="username"]')
        campo_senha = driver.find_element(By.XPATH, '//input[@type="password" or @name="password"]')
        campo_usuario.send_keys(usuario)
        campo_senha.send_keys(senha)
        botao_entrar = driver.find_element(By.XPATH, '//button[contains(text(),"Entrar")]')
        botao_entrar.click()
        time.sleep(4)
        # 2. Acessa log remoto
        log_url = f"http://{usuario}:{senha}@192.168.0.1/2.0/gui/pages/seguranca/log-remoto"
        driver.get(log_url)
        time.sleep(2)
        html = driver.page_source
    finally:
        driver.quit()

    # 3. Extrai linhas da tabela
    soup = BeautifulSoup(html, "html.parser")
    linhas = soup.select("table.table-normal.resp-header tbody tr")

    # 4. Conexão com SQLite
    con = sqlite3.connect(DEFAULT_DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs_modem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            modulo TEXT,
            nivel TEXT,
            mensagem TEXT, 
            UNIQUE(timestamp,modulo,mensagem)
        )
    """)
    novas = 0
    for linha in linhas:
        colunas = linha.find_all("td")
        if colunas and len(colunas) >= 4:
            try:
                timestamp = parse_data_hora(colunas[0].get_text(strip=True))
            except Exception as e:
                print(f"Erro ao converter data: {colunas[0].get_text(strip=True)} | {e}")
                continue
            modulo = colunas[1].get_text(strip=True)
            nivel = colunas[2].get_text(strip=True)
            mensagem = colunas[3].get_text(strip=True)

            print(timestamp, modulo, nivel, mensagem)
            try:
                if modulo != 'SYS':
                    cur.execute(
                        "INSERT INTO logs_modem (timestamp, modulo, nivel, mensagem) VALUES (?, ?, ?, ?)",
                        (timestamp, modulo, nivel, mensagem)
                    )
                    novas += 1
            except sqlite3.IntegrityError as err:
                print(err)
                continue
    con.commit()
    con.close()
    print(f"{novas} novos logs inseridos.")

if __name__ == "__main__":
    while True:
        salvar_logs()
        print("Aguardando 30 segundos para próxima verificação...\n")
        time.sleep(30)