from streaming.db_writer import LATEST_PRICES_UPSERT, RAW_EVENTS_INSERT, write_event


class DummyCursor:
    def __init__(self):
        self.calls = []

    def execute(self, sql, params):
        self.calls.append((sql, params))


def test_write_event_executes_raw_insert_and_latest_upsert():
    cursor = DummyCursor()
    event = {
        "event_id": "BINANCE:trade:BTCUSDT:123",
        "source": "binance",
        "stream": "trade",
        "symbol": "BTCUSDT",
        "event_time": "2026-05-05T16:21:34.123+00:00",
        "price": 63250.12,
        "quantity": 0.015,
        "trade_id": 123,
        "is_buyer_maker": False,
        "payload_json": {"foo": "bar"},
    }

    write_event(cursor, event)

    assert len(cursor.calls) == 2
    assert "ON CONFLICT (event_id) DO NOTHING" in cursor.calls[0][0]
    assert "ON CONFLICT (symbol) DO UPDATE" in cursor.calls[1][0]
    assert cursor.calls[0][1][0] == event["event_id"]
    assert cursor.calls[1][1][0] == event["symbol"]
    assert RAW_EVENTS_INSERT.strip() in cursor.calls[0][0]
    assert LATEST_PRICES_UPSERT.strip() in cursor.calls[1][0]
