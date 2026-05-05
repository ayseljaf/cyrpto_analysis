"""Schema normalization utilities for Binance streaming events."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_trade_event(message: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Binance combined-stream trade payload into internal schema."""
    data = message.get("data", message)

    symbol = data["s"]
    trade_id = int(data["t"])
    event_time = datetime.fromtimestamp(int(data["E"]) / 1000, tz=timezone.utc).isoformat()

    return {
        "event_id": f"BINANCE:trade:{symbol}:{trade_id}",
        "source": "binance",
        "stream": "trade",
        "symbol": symbol,
        "event_time": event_time,
        "price": float(data["p"]),
        "quantity": float(data["q"]),
        "trade_id": trade_id,
        "is_buyer_maker": bool(data["m"]),
        "ingested_at": utc_now_iso(),
        "payload_json": data,
    }
