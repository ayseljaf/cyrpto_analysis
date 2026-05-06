"""Configuration constants for the crypto pipeline DAG."""

from datetime import timedelta

TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "SHIBUSDT",
    "USDCUSDT",
]

POSTGRES_CONN_ID = "crypto_postgres"

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

