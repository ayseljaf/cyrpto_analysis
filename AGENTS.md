<claude-mem-context>
# Memory Context

# [cyrpto_analysis] recent context, 2026-05-05 9:29pm GMT+2

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (17,737t read) | 451,672t work | 96% savings

### May 4, 2026
S34 FastAPI src/ package fully refactored with database.py separation; Task-05 complete, ready for Task-06 Flask (May 4 at 11:26 AM)
S31 Implement crypto_analysis tasks: refactored FastAPI to src/ package, rebuilt and verified container (May 4 at 11:26 AM)
S32 FastAPI src/ package refactor complete and verified; pydantic-settings discussed but deferred (May 4 at 11:26 AM)
S35 Debug and fix crypto_analysis_pipeline DAG — two extract bugs identified and resolved, all 7 extract tasks now succeeding (May 4 at 3:37 PM)
60 4:03p 🔵 DAG topology confirmed live in scheduler — 9 tasks, no import errors
61 " 🟣 First manual DAG run triggered for crypto_analysis_pipeline
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
### May 5, 2026
114 8:28p 🔵 crypto_analysis Project Structure — Pre-Kafka Implementation Baseline
115 8:29p 🟣 Streaming Module Scaffolded — Directories and Schema Normalization Created
116 " 🟣 db_writer.py Created — Idempotent Raw Events Insert + Latest Prices Upsert
117 " 🟣 Binance Kafka Producer Implemented with Auto-Reconnect and Graceful Shutdown
118 " 🟣 Kafka Consumer Implemented — DB-First Commit Ordering, Per-Message Transaction
119 8:30p 🟣 Streaming SQL Migration and Dockerfile Created
120 " 🟣 docker-compose.yml Updated — Kafka Stack and Streaming Services Added
121 " ✅ Zookeeper Healthcheck Removed from docker-compose.yml
122 " 🟣 Dashboard Updated with Real-Time Latest Prices Panel and 5-Second Refresh
123 " 🟣 Unit Tests Created for Schema Normalization and DB Writer
124 8:31p 🔴 tests/conftest.py Patched to Add src/ to sys.path for Streaming Imports
125 " 🟣 Streaming Unit Tests Pass — 2/2 Green; Integration Test Placeholder Added
127 " 🔵 Docker Socket Permission Denied — Stack Cannot Be Deployed from Claude Code Session
128 " 🟣 Docker Stack Deployment Initiated — Kafka Images Pulling Successfully with Escalated Permissions
129 " 🟣 Full Kafka Streaming Stack Deployed Successfully — All Services Started
126 " 🔵 docker-compose.yml Validates Successfully — Minor version Attribute Warning
131 8:32p ✅ README Update — Kafka Streaming Section Added
130 8:34p 🔵 Post-Deploy Verification Commands Blocked — Docker Socket Escalation Not Persistent
132 9:23p ✅ README.md — Kafka Streaming Section Added
133 " 🔵 Docker Socket Permission Denied Without Escalation
134 9:24p 🔵 Dashboard Shows Empty — Airflow Stack Not Running in Streaming-Only Deploy
136 " 🟣 kafka-ui Added and Started — Kafka Topic Browser at localhost:8081
138 " 🔵 kafka-ui Healthy — Connected to Cluster "local", Polling Every 30s
139 " ✅ README.md — kafka-ui URL Added to URLs Table
135 9:25p 🔵 kafka-ui Service Not Defined in docker-compose.yml
137 " 🟣 kafka-ui Container Started Successfully

Access 452k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>