"""PostgreSQL write helpers for stream consumer."""

from __future__ import annotations

import json
from typing import Any, Dict

RAW_EVENTS_INSERT = """
INSERT INTO raw_events (
    event_id,
    source,
    stream,
    symbol,
    event_time,
    price,
    quantity,
    trade_id,
    is_buyer_maker,
    payload_json,
    created_at
) VALUES (%s, %s, %s, %s, %s::timestamptz, %s, %s, %s, %s, %s::jsonb, NOW())
ON CONFLICT (event_id) DO NOTHING
"""

LATEST_PRICES_UPSERT = """
INSERT INTO latest_prices (
    symbol,
    last_price,
    last_quantity,
    last_event_time,
    updated_at
) VALUES (%s, %s, %s, %s::timestamptz, NOW())
ON CONFLICT (symbol) DO UPDATE SET
    last_price = EXCLUDED.last_price,
    last_quantity = EXCLUDED.last_quantity,
    last_event_time = EXCLUDED.last_event_time,
    updated_at = NOW()
WHERE latest_prices.last_event_time IS NULL
   OR EXCLUDED.last_event_time >= latest_prices.last_event_time
"""


def write_event(cursor: Any, event: Dict[str, Any]) -> None:
    """Write an event to raw history and latest-price serving table."""
    cursor.execute(
        RAW_EVENTS_INSERT,
        (
            event["event_id"],
            event["source"],
            event["stream"],
            event["symbol"],
            event["event_time"],
            event["price"],
            event["quantity"],
            event["trade_id"],
            event["is_buyer_maker"],
            json.dumps(event["payload_json"]),
        ),
    )

    cursor.execute(
        LATEST_PRICES_UPSERT,
        (
            event["symbol"],
            event["price"],
            event["quantity"],
            event["event_time"],
        ),
    )
