# API Monitoramento de Rede (api-monitoramento-rede)

Este README descreve o uso da API REST para consulta dos dados de conectividade coletados pelo serviço **netmon**.

## Visão Geral

A API fornece acesso aos registros de ping e HTTP que são armazenados em um banco SQLite compartilhado. Ela roda no container **api-monitoramento-rede** e responde em [**http://localhost:8090**](http://localhost:8090) por padrão.

## Endpoints Disponíveis

### 1. GET `/logs`

Retorna uma lista dos registros de conectividade.

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

- Todos os logs (até 100 entradas):

  ```bash
  curl "http://localhost:8090/logs"
  ```

- Últimos 50 registros de PING bem-sucedidos ao `8.8.8.8`:

  ```bash
  curl "http://localhost:8090/logs?limit=50&target=8.8.8.8&method=PING&status=FAIL"
  ```

- Registros HTTP entre datas específicas:

  ```bash
  curl "http://localhost:8090/logs?method=HTTP&since=2025-06-21T00:00:00&until=2025-06-22T23:59:59"
  ```

### 2. GET `/stats`

Retorna estatísticas agregadas sobre os registros.

**Query Parameters:**

| Parâmetro | Tipo     | Descrição                     |
| --------- | -------- | ----------------------------- |
| `since`   | `string` | Início do período (ISO 8601). |
| `until`   | `string` | Fim do período (ISO 8601).    |

**Resposta:**

```json
{
  "total": 250,
  "success": 240,
  "failure": 10,
  "avg_latency": 85.3
}
```

- **total**: total de registros no período.
- **success**: contagem de registros com `status = OK`.
- **failure**: contagem de registros com `status = FAIL`.
- **avg\_latency**: latência média (ms) apenas dos registros `OK`.

**Exemplo:**

```bash
curl "http://localhost:8090/stats?since=2025-06-22T00:00:00&until=2025-06-22T23:59:59"
```

### 3. Documentação Interativa

Acesse a documentação Swagger UI em:

```
http://localhost:8090/docs
```

ou a Redoc em:

```
http://localhost:8090/redoc
```

## Configuração de Acesso

- **Porta**: 8090 (mapeada no `docker-compose.yml` como `8090:8000`).
- **Variável de ambiente**: `DB_PATH` deve apontar para o arquivo SQLite montado (ex.: `/data/connectivity.db`).

## Exemplos de Integração (Python)

```python
import requests

API = "http://localhost:8090"

# Buscar logs
resp = requests.get(f"{API}/logs", params={
    'limit': 10,
    'status': 'FAIL'
})
logs = resp.json()

# Buscar estatísticas
resp = requests.get(f"{API}/stats", params={
    'since': '2025-06-22T00:00:00',
    'until': '2025-06-22T23:59:59'
})
stats = resp.json()
```

## Feedback

Para melhorias ou dúvidas, abra uma issue no repositório ou contate o desenvolvedor.

