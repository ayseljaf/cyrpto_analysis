# Azure Production Deployment Blueprint

This document defines a production-grade Azure target architecture for this repository.

## 1) Target Architecture

- Container runtime: **AKS** (Azure Kubernetes Service)
- Container registry: **ACR** (Azure Container Registry)
- Database: **Azure Database for PostgreSQL Flexible Server** (+ TimescaleDB extension)
- Streaming: **Azure Event Hubs (Kafka endpoint)**
- Workflow orchestration: **Managed Airflow** (Astronomer on Azure) or self-hosted Airflow on AKS
- Secrets: **Azure Key Vault**
- Identity: **Managed Identity** + Entra ID workload identity
- Ingress/TLS: **Application Gateway Ingress Controller** + Key Vault certs
- Observability: **Azure Monitor + Log Analytics + Managed Prometheus/Grafana**

Data flow:

1. `stream-producer` reads Binance WebSocket and publishes to Kafka topic (`binance.trades.raw`) on Event Hubs.
2. `stream-consumer` reads topic and writes to PostgreSQL (`raw_events`, `latest_prices`).
3. `fastapi` and `dashboard` read from PostgreSQL.
4. Airflow runs scheduled analytics + DQ jobs, reading/writing PostgreSQL tables.

## 2) Azure Service Mapping

- Current Docker `kafka` + `zookeeper` -> **Azure Event Hubs Standard/Premium** (Kafka protocol)
- Current `timescaledb` container -> **Azure PostgreSQL Flexible Server**
- Current app containers (`producer`, `consumer`, `fastapi`, `dashboard`) -> **AKS deployments**
- Current local `.env` secrets -> **Key Vault secrets mounted/injected**
- Current Airflow compose services:
  - Preferred: **Astronomer managed Airflow**
  - Alternative: **Helm deployment on AKS with CeleryExecutor + Redis/PG backend**

## 3) Network and Security Baseline

- Single hub-spoke VNet or dedicated app VNet
- Private endpoints for PostgreSQL, Event Hubs, Key Vault, ACR
- Disable public network access where possible
- NSGs allow only required east-west traffic
- AKS API private cluster (recommended)
- TLS enforced for all DB/Kafka/API connections
- Store no credentials in git; all secrets in Key Vault
- Use managed identity for Key Vault and ACR pull

## 4) Production Sizing (Initial)

- AKS node pools:
  - `system`: 3 nodes (e.g., D4s_v5)
  - `apps`: autoscaling 3-10 nodes (e.g., D4s_v5)
- Producer replicas: 2 (HPA on CPU + reconnect metrics)
- Consumer replicas: 2-6 (scale by consumer lag)
- FastAPI replicas: 2-6 (HPA on CPU/RPS)
- Dashboard replicas: 2 (or internal-only if not public)
- PostgreSQL:
  - HA enabled
  - PITR enabled
  - connection pooling (PgBouncer)
- Event Hubs:
  - 3+ partitions for trade topic
  - retention 3-7 days for replay

## 5) App Configuration Changes Required

- Replace local env vars with `APP_*` + Key Vault-backed values
- Add robust readiness/liveness probes for all services
- Add structured logs (JSON) and request IDs
- Add consumer lag/throughput metrics endpoint
- Keep idempotent DB writes (`ON CONFLICT`) as currently implemented
- Optional: add DLQ topic (`binance.trades.dlq`) for poison messages

## 6) CI/CD Blueprint (GitHub Actions)

Per commit to `main`:

1. Run tests (`pytest` unit + selected integration)
2. Build images for:
   - `stream-producer`
   - `stream-consumer`
   - `fastapi`
   - `dashboard`
3. Scan images (Trivy/Defender)
4. Push to ACR with immutable tags
5. Deploy to AKS via Helm/Kustomize
6. Run smoke checks:
   - `raw_events` count increases
   - `latest_prices` freshness within SLA
   - API health endpoints green

## 7) Terraform Module Layout

```text
infra/terraform/
  envs/prod/
    main.tf
    variables.tf
    outputs.tf
    providers.tf
    terraform.tfvars.example
  modules/
    network/
    acr/
    aks/
    postgres/
    kafka/
    airflow/
    keyvault/
    monitoring/
```

Module responsibilities:

- `network`: VNet, subnets, NSGs, private DNS zones
- `acr`: registry + private access
- `aks`: cluster, node pools, workload identity, ingress add-ons
- `postgres`: flexible server, HA, backups, firewall/private endpoint
- `kafka`: Event Hubs namespace/hub/topic-equivalent, auth policies
- `airflow`: managed Airflow integration points (or AKS namespace scaffolding)
- `keyvault`: secrets, access policies/RBAC
- `monitoring`: Log Analytics, Azure Monitor alerts, dashboards

## 8) Migration Plan from Local to Azure

1. Provision infra with Terraform in a new Azure subscription/resource group.
2. Push application images to ACR.
3. Deploy PostgreSQL schema (`setup_tables.sql`, `create_analysis_tables.sql`, `create_streaming_tables.sql`).
4. Deploy `stream-consumer` first; verify DB write path.
5. Deploy `stream-producer`; verify event flow + lag.
6. Deploy API and dashboard; validate user paths.
7. Deploy Airflow and configure `crypto_postgres` connection to Azure PostgreSQL.
8. Cut over DNS and enable alerts/on-call.

## 9) Minimum Production Alerts

- Consumer lag above threshold (5m sustained)
- No new rows in `raw_events` for >2 minutes
- `latest_prices.updated_at` stale for >60s
- Airflow DAG failure rate > threshold
- PostgreSQL CPU/storage/connection saturation
- AKS pod restart loops and failed probes

## 10) Runbook Commands (Post-Deploy)

- Check consumer lag (Event Hubs metrics / Kafka client metrics)
- Check freshness:
  - `SELECT MAX(created_at) FROM raw_events;`
  - `SELECT symbol, updated_at FROM latest_prices;`
- Restart deployment safely:
  - `kubectl rollout restart deployment/stream-consumer -n crypto`

