# API Monitoramento de Rede (api-monitoramento-rede)

---
## ⚡ Público-alvo

> Esta aplicação foi **desenvolvida especialmente para clientes CLARO Residencial banda larga** que desejam monitorar a qualidade de sua conexão, consultar logs do modem e realizar medições históricas da rede.

---

## 🌐 Fonte dos Dados de Velocidade

O módulo de monitoramento de velocidade (**monitor_qos**) utiliza o serviço oficial da Netflix: [**fast.com**](https://fast.com/)  
Todos os resultados de download, upload e latência são obtidos a partir desse serviço.

> **Nota:** O uso do fast.com como fonte garante medições compatíveis com padrões globais de performance de rede.

---

## Visão Geral

## 🚦 Documentação Interativa com Swagger UI

Para facilitar testes e integração, a API fornece uma documentação interativa gerada automaticamente pelo Swagger.

- Basta acessar: [http://localhost:8090/docs](http://localhost:8090/docs)
- Você pode **testar todos os endpoints**, ver exemplos, schemas e respostas diretamente pelo navegador.

![Exemplo Swagger UI](https://fastapi.tiangolo.com/img/index/index-02-swagger-02.png)

Alternativamente, a documentação Redoc está disponível em [http://localhost:8090/redoc](http://localhost:8090/redoc).

---

> **Dica:**  
> O Swagger UI é ótimo para aprendizado, validação rápida e até para explorar parâmetros de busca, como filtros por data, módulo, mensagem, etc.

---

A API fornece acesso aos registros de conectividade (ping, HTTP) e também medições de velocidade de internet (download, upload, latência) armazenados em um banco SQLite compartilhado.  
Ela roda no container **api-monitoramento-rede** e responde em [**http://localhost:8090**](http://localhost:8090) por padrão.

## Endpoints Disponíveis

### 1. GET `/logs`

Retorna uma lista dos registros de conectividade (ping e HTTP).

**Query Parameters:**

| Parâmetro | Tipo     | Padrão | Descrição                                                                         |
| --------- | -------- | ------ | --------------------------------------------------------------------------------- |
| `limit`   | `int`    | 100    | Número máximo de registros retornados (deve ser > 0).                             |
| `target`  | `string` | —      | Filtra pelo campo `target` (ex.: `8.8.8.8`).                                      |
| `method`  | `string` | —      | Filtra por método de checagem (`PING` ou `HTTP`).                                 |
| `status`  | `string` | —      | Filtra por resultado (`OK` ou `FAIL`).                                            |
| `since`   | `string` | —      | Filtra registros com `timestamp >= since` (ISO 8601, ex.: `2025-06-22T00:00:00`). |
| `until`   | `string` | —      | Filtra registros com `timestamp <= until` (ISO 8601).                             |

**Exemplos de uso:**

```bash
curl "http://localhost:8090/logs"
```

```bash
curl "http://localhost:8090/logs?limit=50&target=8.8.8.8&method=PING&status=FAIL"
```

```bash
curl "http://localhost:8090/logs?method=HTTP&since=2025-06-21T00:00:00&until=2025-06-22T23:59:59"
```

---

### 2. GET `/monitor_qos`

Retorna uma lista de medições de qualidade de sinal da internet, como download, upload e latência.

**Query Parameters:**

| Parâmetro | Tipo     | Descrição                                                         |
| --------- | -------- | ----------------------------------------------------------------- |
| `since`   | `string` | (opcional) Data/hora inicial no formato ISO 8601                  |
| `until`   | `string` | (opcional) Data/hora final no formato ISO 8601                    |

**Exemplo de uso – obter todos os testes do mês de maio de 2025:**
```bash
curl "http://localhost:8090/monitor_qos?since=2025-05-01T00:00:00&until=2025-05-31T23:59:59"
```

#### Resposta típica:
```json
[
  {
    "id": 1,
    "timestamp": "2025-05-10T15:32:44-03:00",
    "download": 37.4,
    "upload": 6.1,
    "latency": 19,
    "isp": "Claro",
    "ip": "177.64.159.167"
  },
  ...
]
```

---

### 3. GET `/stats`

Retorna estatísticas agregadas sobre os registros de conectividade.

**Query Parameters:**

| Parâmetro | Tipo     | Descrição                     |
| --------- | -------- | ----------------------------- |
| `since`   | `string` | Início do período (ISO 8601). |
| `until`   | `string` | Fim do período (ISO 8601).    |

**Exemplo:**

```bash
curl "http://localhost:8090/stats?since=2025-06-22T00:00:00&until=2025-06-22T23:59:59"
```

---

### 4. Documentação Interativa

Acesse a documentação Swagger UI em:

```
http://localhost:8090/docs
```
ou a Redoc em:

```
http://localhost:8090/redoc
```

---

## Exemplo de Consulta dos Downloads por Mês

Para consultar todos os downloads do mês 5 (maio), use o parâmetro de data no formato:

```
/monitor_qos?since=2025-05-01T00:00:00&until=2025-05-31T23:59:59
```

#### Exemplo com Python:
```python
import requests
from datetime import datetime

API = "http://localhost:8090"

since = "2025-05-01T00:00:00"
until = "2025-05-31T23:59:59"
resp = requests.get(f"{API}/monitor_qos", params={
    "since": since,
    "until": until
})
result = resp.json()
downloads = [row['download'] for row in result]
print(downloads)
```

---

## Configuração de Acesso

- **Porta**: 8090 (mapeada no `docker-compose.yml` como `8090:8090`).
- **Variável de ambiente**: `DB_PATH` deve apontar para o arquivo SQLite montado (ex.: `/data/connectivity.db`).

---

---

## Observações Finais

- **Fonte dos dados QoS:** [fast.com](https://fast.com/) – solução oficial de medição da Netflix
- **Público-alvo:** Usuários residenciais CLARO banda larga
- **Swagger UI:** Documentação online em `/docs` para todos os endpoints

## Feedback

Para melhorias ou dúvidas, abra uma issue no repositório ou contate o desenvolvedor.

# API Monitoramento de Rede (api-monitoramento-rede)

Este README descreve o uso da API REST para consulta dos dados de conectividade e análise de qualidade de sinal coletados pelo serviço **netmon**, pelo monitor de QoS **e pelos logs do modem**.

## Visão Geral

A API fornece acesso aos registros de conectividade (ping, HTTP), medições de velocidade de internet (download, upload, latência) e logs do modem (ex: eventos de rede) armazenados em um banco SQLite compartilhado.  
Ela roda no container **api-monitoramento-rede** e responde em [**http://localhost:8090**](http://localhost:8090) por padrão.

---

## Endpoints Disponíveis

### 1. GET `/logs`

Retorna uma lista dos registros de conectividade (ping e HTTP).

**Query Parameters:**

| Parâmetro | Tipo     | Padrão | Descrição                                                                         |
| --------- | -------- | ------ | --------------------------------------------------------------------------------- |
| `limit`   | `int`    | 100    | Número máximo de registros retornados (deve ser > 0).                             |
| `target`  | `string` | —      | Filtra pelo campo `target` (ex.: `8.8.8.8`).                                      |
| `method`  | `string` | —      | Filtra por método de checagem (`PING` ou `HTTP`).                                 |
| `status`  | `string` | —      | Filtra por resultado (`OK` ou `FAIL`).                                            |
| `since`   | `string` | —      | Filtra registros com `timestamp >= since` (ISO 8601, ex.: `2025-06-22T00:00:00`). |
| `until`   | `string` | —      | Filtra registros com `timestamp <= until` (ISO 8601).                             |

**Exemplo:**
```bash
curl "http://localhost:8090/logs?method=HTTP&since=2025-06-21T00:00:00&until=2025-06-22T23:59:59"
```

---

### 2. GET `/monitor_qos`

Retorna uma lista de medições de qualidade de sinal da internet, como download, upload e latência.

**Query Parameters:**

| Parâmetro | Tipo     | Descrição                                                         |
| --------- | -------- | ----------------------------------------------------------------- |
| `since`   | `string` | (opcional) Data/hora inicial no formato ISO 8601                  |
| `until`   | `string` | (opcional) Data/hora final no formato ISO 8601                    |

**Exemplo para obter todos os testes do mês de maio de 2025:**
```bash
curl "http://localhost:8090/monitor_qos?since=2025-05-01T00:00:00&until=2025-05-31T23:59:59"
```

#### Resposta típica:
```json
[
  {
    "id": 1,
    "timestamp": "2025-05-10T15:32:44-03:00",
    "download": 37.4,
    "upload": 6.1,
    "latency": 19,
    "isp": "Claro",
    "ip": "177.64.159.167"
  },
  ...
]
```

---

### 3. GET `/logs_modem`

Retorna os logs do modem coletados automaticamente (ex: eventos, falhas de rede, mensagens do sistema).

**Query Parameters:**

| Parâmetro    | Tipo        | Descrição                                                                 |
| ------------ | ----------- | ------------------------------------------------------------------------- |
| `since`      | `datetime`  | (opcional) Data/hora inicial (ISO 8601, ex: `2025-06-21T00:00:00`)        |
| `until`      | `datetime`  | (opcional) Data/hora final (ISO 8601, ex: `2025-06-22T23:59:59`)          |
| `modulo`     | `string`    | (opcional) Filtra por módulo do log (ex: `NET`, `LAN`, etc)               |
| `nivel`      | `string`    | (opcional) Filtra por nível (`INFO`, `WARN`, `ERROR`, etc)                |
| `mensagem`   | `string`    | (opcional) Busca por palavras na mensagem                                 |
| `limit`      | `int`       | (opcional) Limite máximo de registros retornados (ex: `100`)              |

**Exemplos de uso:**

- Todos os logs do modem do mês de junho de 2025:
```bash
curl "http://localhost:8090/logs_modem?since=2025-06-01T00:00:00&until=2025-06-30T23:59:59"
```

- Filtrar por módulo e nível:
```bash
curl "http://localhost:8090/logs_modem?modulo=NET&nivel=ERROR"
```

- Filtrar por mensagem contendo "queda de energia":
```bash
curl "http://localhost:8090/logs_modem?mensagem=queda de energia"
```

---

### 4. GET `/stats`

Retorna estatísticas agregadas sobre os registros de conectividade.

| Parâmetro | Tipo     | Descrição                     |
| --------- | -------- | ----------------------------- |
| `since`   | `string` | Início do período (ISO 8601). |
| `until`   | `string` | Fim do período (ISO 8601).    |

**Exemplo:**
```bash
curl "http://localhost:8090/stats?since=2025-06-22T00:00:00&until=2025-06-22T23:59:59"
```

---

### 5. Documentação Interativa

Acesse a documentação Swagger UI em:

```
http://localhost:8090/docs
```
ou a Redoc em:

```
http://localhost:8090/redoc
```

---

## Exemplo de Consulta dos Downloads por Mês

Para consultar todos os downloads do mês 5 (maio), use:

```bash
curl "http://localhost:8090/monitor_qos?since=2025-05-01T00:00:00&until=2025-05-31T23:59:59"
```

#### Exemplo com Python:
```python
import requests
from datetime import datetime

API = "http://localhost:8090"
since = "2025-05-01T00:00:00"
until = "2025-05-31T23:59:59"
resp = requests.get(f"{API}/monitor_qos", params={
    "since": since,
    "until": until
})
result = resp.json()
downloads = [row['download'] for row in result]
print(downloads)
```

---

## Exemplo de Consulta dos Logs do Modem com múltiplos filtros

```bash
curl "http://localhost:8090/logs_modem?modulo=NET&nivel=ERROR&since=2025-06-10T00:00:00"
```

#### Exemplo em Python:
```python
resp = requests.get(f"{API}/logs_modem", params={
    "modulo": "NET",
    "nivel": "ERROR",
    "since": "2025-06-10T00:00:00"
})
print(resp.json())
```

---

## Configuração de Acesso

- **Porta**: 8090 (mapeada no `docker-compose.yml` como `8090:8090`).
- **Variável de ambiente**: `DB_PATH` deve apontar para o arquivo SQLite montado (ex.: `/data/connectivity.db`).

---

## Testando Endpoints

### Usando curl (testes rápidos):

```bash
# Obter 20 logs do modem do módulo 'NET' de hoje
curl "http://localhost:8090/logs_modem?modulo=NET&limit=20&since=2025-07-02T00:00:00"

# Baixar todas as medições QoS do mês de junho
curl "http://localhost:8090/monitor_qos?since=2025-06-01T00:00:00&until=2025-06-30T23:59:59"
```

### Usando Python requests:

```python
# Buscar logs do modem filtrando por mensagem
resp = requests.get(f"{API}/logs_modem", params={
    "mensagem": "queda de energia",
    "since": "2025-06-01T00:00:00"
})
print(resp.json())
```

---

## Feedback

Para melhorias ou dúvidas, abra uma issue no repositório ou contate o desenvolvedor.

---