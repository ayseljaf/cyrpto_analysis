<claude-mem-context>
# Memory Context

# [cyrpto_analysis] recent context, 2026-05-05 5:59pm GMT+2

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (17,201t read) | 383,963t work | 96% savings

### May 3, 2026
35 10:32p 🟣 docker/docker-compose.yml Created — Main Stack with TimescaleDB, Redis, APIs, Dashboard on crypto_network
36 " 🟣 Task-03 Complete: docker/ Directory Fully Populated, Both Compose Files YAML-Valid
37 " 🔐 docker/.env.docker Not Gitignored — Real Credentials Will Be Committed
38 10:33p 🔴 .gitignore Updated to Exclude docker/.env.docker
39 10:43p 🔵 TimescaleDB Container Running as docker-timescaledb-1 But psql Auth Failing
40 10:44p 🔵 TimescaleDB Container Running — crypto_db Initialized with crypto_user as Owner
41 " 🔵 Two SQL Files: setup_tables.sql Creates crypto_prices, create_analysis_tables.sql Creates DAG Tables
42 10:49p 🟣 Task-04 Complete: All Database Tables Migrated to crypto_db on docker-timescaledb-1
### May 4, 2026
43 10:25a 🔵 Crypto Analysis Task Audit: Implementation Status
44 10:42a 🔵 Task-04 Spec: DB Setup Details and Table Count Discrepancy
45 11:00a 🔵 airflow_db Contains Airflow Metadata Tables; crypto_db Indexes Verified
46 11:02a 🔵 Task-01 Spec: reference_files/ Never in Planned Directory Structure
47 " 🔵 Task-01 and Task-02 Actual State Verified; .env.docker Contents Confirmed
48 11:04a 🔵 Task-02 DAG Syntax and Best Practices Verified
49 " 🟣 FastAPI App Created at Project Root with Pydantic Models and DI
50 " 🟣 docker/Dockerfile.fastapi Created with Python 3.11 and SQLAlchemy 2.x
51 " 🔵 docker-compose.yml Already Contains Service Stubs for All API Services
53 11:08a 🔵 docker/Dockerfile.fastapi Not Visible in Directory Listing After Write
55 11:10a 🟣 FastAPI Service Live — Endpoints Returning Real Data from TimescaleDB
52 11:11a ✅ docker-compose.yml fastapi Service Updated to Use Dockerfile.fastapi
54 11:13a 🟣 FastAPI Docker Image Built Successfully
S34 FastAPI src/ package fully refactored with database.py separation; Task-05 complete, ready for Task-06 Flask (May 4 at 11:26 AM)
S31 Implement crypto_analysis tasks: refactored FastAPI to src/ package, rebuilt and verified container (May 4 at 11:26 AM)
S32 FastAPI src/ package refactor complete and verified; pydantic-settings discussed but deferred (May 4 at 11:26 AM)
56 11:26a 🔄 FastAPI src/ package split: src/database.py extracted
S35 Debug and fix crypto_analysis_pipeline DAG — two extract bugs identified and resolved, all 7 extract tasks now succeeding (May 4 at 3:37 PM)
57 3:50p 🔵 DAG extract task has no idempotency — appends duplicates on re-run
58 " 🔵 DAG structure: 521 lines, 7 tasks, dynamic mapping, sensors, data quality checks
59 " 🔵 Airflow stack healthy, DAG loaded with no import errors
60 4:03p 🔵 DAG topology confirmed live in scheduler — 9 tasks, no import errors
61 " 🟣 First manual DAG run triggered for crypto_analysis_pipeline
62 " 🔵 All 7 extract_crypto_data tasks failing and retrying on first DAG run
63 4:08p 🔵 airflow tasks logs command doesn't exist in this Airflow version
64 4:17p 🔵 Root cause of extract failures: crypto_postgres Airflow connection not registered
65 4:40p 🔵 extract_crypto_data fails with UniqueViolation on re-run — no idempotency guard confirmed
66 8:39p 🔴 Fixed extract_crypto_data UniqueViolation — added delete-before-insert idempotency
67 " 🔵 Airflow 2.8.1 `tasks clear` Has No `--dag-run-id` Flag
68 " 🔵 Fresh DAG Run Triggered but Tasks Stuck at `None` State
69 9:33p 🔵 DAG Runs Stuck Queued Due to Concurrent `running` Run Consuming max_active_runs Slot
70 9:37p 🔵 New Bug: SHIBUSDT Extract Fails with `NumericValueOutOfRange` on `volume` Column
71 " 🔵 Extract Task Idempotency Fix Confirmed Working for 6/7 Symbols
72 " 🔵 `crypto_prices` Table Schema: `volume` Column is `NUMERIC(20,8)` — Overflows for SHIB
73 " 🔴 Widened `crypto_prices` Volume Columns from `NUMERIC(20,8)` to `NUMERIC(30,8)`
74 " 🔵 ALTER TABLE on `crypto_prices` Returns Success but Column Types Unchanged
S36 Full pipeline debugged and running — now exploring project structure to plan Task-06 Flask, Task-07 dashboard, schema fix, and from-scratch startup runbook (May 4 at 9:45 PM)
75 9:47p 🔵 Downstream Tasks Stuck in `upstream_failed` — Won't Auto-Recover After Extract Fix
76 " 🔵 `airflow tasks clear` with `-t` Task Regex Also a No-Op — Downstream Tasks Remain Stuck
77 9:49p 🟣 Full `crypto_analysis_pipeline` Run Completed End-to-End Successfully
78 " 🔵 Docker Directory Structure: Two Compose Files, Two Dockerfiles
79 " 🔵 Full docker-compose.yml Service Map and SQL Schema File Locations Found
S37 Crypto analysis project: audit ai-docs/tasks/, implement missing pieces — currently completing docker-compose consolidation and pending Task-06 Flask service, Task-07 dashboard DB update, Task-08 integration tests (May 4 at 9:50 PM)
80 9:54p 🔵 `flask` Service in Compose Uses Generic `docker/Dockerfile`, Not `Dockerfile.flask`
81 " 🔵 Generic `docker/Dockerfile` Missing — Flask, Dashboard, Data Collector Services Will Fail to Build
82 " ✅ docker-compose.yml Completely Rewritten — Two Compose Files Merged, Auto-Connection, db-init Service Added
S38 Crypto analysis project: docker-compose.yml consolidated + validated, user asked for startup/stop/reset commands reference (May 4 at 9:55 PM)
S40 Docker compose stack startup failure — Redis crash + env var expansion root cause identified, fix is --env-file .env.docker CLI flag (May 4 at 10:00 PM)
83 10:15p 🔵 Redis fatal startup failure — empty REDIS_PASSWORD env var
84 " ✅ README.md rewritten — replaced Astronomer boilerplate with actual project docs
S39 Docker compose stack startup — diagnosed Redis fatal crash and env var expansion issue, identified fix using --env-file flag (May 4 at 10:15 PM)
S41 README.md rewritten from Astronomer boilerplate to actual project documentation covering stack, startup, URLs, API endpoints (May 4 at 10:19 PM)
**Investigated**: - README.md: confirmed it was pure Astronomer CLI boilerplate from `astro dev init` with no project-specific content
    - docker compose logs (timescaledb, redis): timescaledb healthy; redis crashing with "requirepass wrong number of arguments" due to empty REDIS_PASSWORD

**Learned**: - `env_file:` in compose service = vars inside container; `--env-file` CLI flag = vars for YAML interpolation at parse time — different mechanisms
    - Redis 7.4.7 fatally rejects empty `requirepass` argument — no graceful fallback
    - Must always use `docker compose --env-file .env.docker [subcommand]` for this project
    - Project was initialized with `astro dev init` (Astronomer CLI) but now uses custom docker-compose.yml

**Completed**: - README.md: fully rewritten — stack description, quick start with correct `--env-file .env.docker` flag, stop/restart commands, service URLs table (Airflow :8080, FastAPI :8000/docs, Flower :5555), all 5 API endpoints documented, project structure
    - Root cause of Redis startup failure identified: missing `--env-file .env.docker` on docker compose commands
    - Earlier sessions: docker-compose.yml unified, db-init service, AIRFLOW_CONN_CRYPTO_POSTGRES, FastAPI src/ refactor, DAG idempotency fix, NUMERIC(30,8) SHIB fix

**Next Steps**: - Run `docker compose --env-file .env.docker down && docker compose --env-file .env.docker up -d` to verify full stack healthy
    - Remaining cleanup: remove `version: '3.8'` from docker-compose.yml, update sql/setup_tables.sql volume cols to NUMERIC(30,8), delete stale docker-compose.airflow.yml
    - Task-06: Flask service (crypto_api_flask.py + Dockerfile.flask)
    - Task-07: crypto_dashboard.py PostgreSQL migration
    - Task-08: integration tests in tests/integration/


Access 384k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>