# Crypto Analysis Pipeline

Daily ETL pipeline that pulls cryptocurrency price data from Binance, stores it in TimescaleDB, and exposes it via a FastAPI service.
It now also includes a Kafka streaming path for near-real-time dashboard prices.

**Pairs:** BTC, ETH, SOL, ADA, DOGE, SHIB, USDC

## DAG Runs
![alt text](https://github.com/ayseljaf/cyrpto_analysis/blob/main/docs/images/Screenshot%202026-05-05%20at%2014.37.34.png)

## Dashboard
![alt text](https://github.com/ayseljaf/cyrpto_analysis/blob/main/docs/images/Screenshot%202026-05-05%20at%2015.07.46.png)

## Kafka UI
![alt text](https://github.com/ayseljaf/cyrpto_analysis/blob/main/docs/images/Screenshot%202026-05-05%20at%2021.42.22.png)

## Stack

- **Airflow** (CeleryExecutor) — orchestrates daily extraction and analysis
- **TimescaleDB** — stores raw prices and computed statistics
- **FastAPI** — REST API over the processed data
- **Dash Dashboard** — browser UI for monthly statistics, weekly changes, and overall metrics
- **Redis** — Celery broker
- **Kafka + ZooKeeper** — real-time trade stream transport from producer to consumer

## Kafka Streaming (Brief)

- `stream-producer` connects to Binance WebSocket trades and publishes normalized events to Kafka topic `binance.trades.raw`.
- Kafka buffers and distributes these events reliably (decouples ingest from DB writes).
- `stream-consumer` reads that topic and writes:
  - `raw_events` (append-only event history, idempotent on `event_id`)
  - `latest_prices` (upsert per symbol for real-time dashboard panel)
- Dashboard reads `latest_prices` for near-real-time last price updates, while Airflow remains focused on scheduled analytics jobs.

## Quick Start

```bash
cd docker
docker compose --env-file .env.docker up -d
```

Wait ~60s for all services to become healthy, then trigger the pipeline:

```bash
docker exec docker-airflow-scheduler-1 airflow dags trigger crypto_analysis_pipeline
```

## Stop / Restart

```bash
# Stop (keep data)
docker compose --env-file .env.docker down

# Full reset (wipe volumes)
docker compose --env-file .env.docker down -v

# Restart
docker compose --env-file .env.docker up -d
```

## URLs

| Service        | URL                      | Credentials   |
|----------------|--------------------------|---------------|
| Airflow UI     | http://localhost:8080    | admin / admin |
| FastAPI docs   | http://localhost:8000/docs |             |
| Dashboard      | http://localhost:8050    |               |
| Kafka UI       | http://localhost:8081    |               |
| Flower         | http://localhost:5555    |               |

## API Endpoints

```
GET /health
GET /cryptocurrencies
GET /api/monthly-statistics?symbol=BTCUSDT&months=12
GET /api/weekly-changes?symbol=BTCUSDT&days=30
GET /api/overall-statistics?symbol=BTCUSDT
```

## Project Structure

```
dags/            Airflow DAG (crypto_pipeline_dag.py)
src/             FastAPI app (main.py, schemas.py, database.py)
src/dashboard/   Dash dashboard app
sql/             DB setup scripts
docker/          Dockerfiles + docker-compose.yml
logs/            Airflow task logs
```

## Requirements

- Docker + Docker Compose
- `docker/.env.docker` with credentials (see `.env.docker.example` if provided)
