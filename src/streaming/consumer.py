"""Kafka consumer writing stream events into TimescaleDB."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
from typing import Any

import psycopg2
from kafka import KafkaConsumer

from streaming.db_writer import write_event

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("stream-consumer")

RUNNING = True


def _signal_handler(signum: int, _frame: Any) -> None:
    global RUNNING
    RUNNING = False
    logger.info("received signal=%s, shutting down", signum)


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        os.getenv("KAFKA_TOPIC_TRADES", "binance.trades.raw"),
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        group_id=os.getenv("KAFKA_CONSUMER_GROUP", "crypto-stream-consumer"),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=2000,
    )


def db_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "timescaledb"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "crypto_db"),
        user=os.getenv("POSTGRES_USER", "crypto_user"),
        password=os.getenv("POSTGRES_PASSWORD", "crypto_password"),
    )


def main() -> int:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    consumer = build_consumer()
    conn = db_conn()
    conn.autocommit = False

    logger.info("consumer started")

    try:
        while RUNNING:
            for msg in consumer:
                if not RUNNING:
                    break
                event = msg.value
                try:
                    with conn.cursor() as cursor:
                        write_event(cursor, event)
                    conn.commit()
                    consumer.commit()
                except Exception:
                    conn.rollback()
                    logger.exception("failed to process event_id=%s", event.get("event_id"))
    finally:
        consumer.close()
        conn.close()
        logger.info("consumer stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
