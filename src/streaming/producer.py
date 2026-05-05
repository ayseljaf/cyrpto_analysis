"""Kafka producer that streams Binance trade ticks."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from typing import Any, Dict

from kafka import KafkaProducer
from websocket import WebSocketApp

from streaming.schema import normalize_trade_event

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("stream-producer")

RUNNING = True


def _signal_handler(signum: int, _frame: Any) -> None:
    global RUNNING
    RUNNING = False
    logger.info("received signal=%s, shutting down", signum)


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        linger_ms=50,
        retries=10,
    )


def on_message(producer: KafkaProducer, topic: str, raw: str) -> None:
    payload: Dict[str, Any] = json.loads(raw)
    event = normalize_trade_event(payload)
    producer.send(topic, value=event)


def main() -> int:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    streams = os.getenv("BINANCE_STREAMS", "btcusdt@trade,ethusdt@trade")
    topic = os.getenv("KAFKA_TOPIC_TRADES", "binance.trades.raw")
    ws_url = f"wss://stream.binance.com:9443/stream?streams={streams.replace(',', '/')}"

    producer = build_producer()
    logger.info("starting producer streams=%s topic=%s", streams, topic)

    def _on_message(_ws: WebSocketApp, message: str) -> None:
        on_message(producer, topic, message)

    while RUNNING:
        ws = WebSocketApp(
            ws_url,
            on_message=_on_message,
            on_error=lambda _ws, err: logger.warning("websocket error=%s", err),
            on_close=lambda _ws, code, msg: logger.info("websocket closed code=%s msg=%s", code, msg),
        )
        ws.run_forever(ping_interval=20, ping_timeout=10)
        if RUNNING:
            logger.info("reconnecting websocket in 3s")
            time.sleep(3)

    producer.flush()
    producer.close()
    logger.info("producer stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
