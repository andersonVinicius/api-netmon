# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
#
# driver = webdriver.Chrome()
#
# # 1. Login pelo formulário normal
# driver.get("http://192.168.0.1/2.0/gui/login")
# time.sleep(2)
# usuario = "CLARO_57FC9E"
# senha = "@1f0469023aa647N"
#
# campo_usuario = driver.find_element(By.XPATH, '//input[@type="text" or @name="username"]')
# campo_senha = driver.find_element(By.XPATH, '//input[@type="password" or @name="password"]')
# campo_usuario.send_keys(usuario)
# campo_senha.send_keys(senha)
# botao_entrar = driver.find_element(By.XPATH, '//button[contains(text(),"Entrar")]')
# botao_entrar.click()
#
# time.sleep(4)  # espere login concluir
#
# # 2. Agora navega para a URL do log remoto com Basic Auth embutido
# log_url = f"http://{usuario}:{senha}@192.168.0.1/2.0/gui/pages/seguranca/log-remoto"
# driver.get(log_url)
# time.sleep(3)
#
# with open("log_remoto.html", "w", encoding="utf-8") as f:
#     f.write(driver.page_source)
#
# print("Página salva.")
#
#
# with open("log_remoto.html", encoding="utf-8") as f:
#     soup = BeautifulSoup(f, "html.parser")
#
# linhas = soup.select("table.table-normal.resp-header tbody tr")
# for linha in linhas:
#     colunas = linha.find_all("td")
#     if colunas:
#         data_hora = colunas[0].get_text(strip=True)
#         modulo = colunas[1].get_text(strip=True)
#         nivel = colunas[2].get_text(strip=True)
#         mensagem = colunas[3].get_text(strip=True)
#         print(f"{data_hora} | {modulo} | {nivel} | {mensagem}")
#
# # driver.quit()


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time



while True:
    usuario = "CLARO_57FC9E"
    senha = "@1f0469023aa647N"

    driver = webdriver.Chrome()

    # 1. Login pelo formulário normal
    driver.get("http://192.168.0.1/2.0/gui/login")
    time.sleep(2)

    campo_usuario = driver.find_element(By.XPATH, '//input[@type="text" or @name="username"]')
    campo_senha = driver.find_element(By.XPATH, '//input[@type="password" or @name="password"]')
    campo_usuario.send_keys(usuario)
    campo_senha.send_keys(senha)
    botao_entrar = driver.find_element(By.XPATH, '//button[contains(text(),"Entrar")]')
    botao_entrar.click()

    time.sleep(4)  # espere login concluir
    # 2. Agora navega para a URL do log remoto
    # # 2. Agora navega para a URL do log remoto com Basic Auth embutido
    log_url = f"http://{usuario}:{senha}@192.168.0.1/2.0/gui/pages/seguranca/log-remoto"
    driver.get(log_url)
    time.sleep(3)

    # Salva HTML
    with open("log_remoto.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print("Página salva.")

    with open("log_remoto.html", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    linhas = soup.select("table.table-normal.resp-header tbody tr")
    print("-" * 60)
    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) == 4:
            data_hora = colunas[0].get_text(strip=True)
            modulo = colunas[1].get_text(strip=True)
            nivel = colunas[2].get_text(strip=True)
            mensagem = colunas[3].get_text(strip=True)
            print(f"{data_hora} | {modulo} | {nivel} | {mensagem}")
    print("Aguardando 30 segundos...\n")
    time.sleep(30)

# driver.quit()  # Você pode colocar aqui se quiser encerrar manualmente