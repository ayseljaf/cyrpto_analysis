from streaming.schema import normalize_trade_event


def test_normalize_trade_event_creates_deterministic_event_id():
    message = {
        "stream": "btcusdt@trade",
        "data": {
            "e": "trade",
            "E": 1714928494123,
            "s": "BTCUSDT",
            "t": 123456789,
            "p": "63250.12",
            "q": "0.015",
            "m": False,
        },
    }

    event = normalize_trade_event(message)

    assert event["event_id"] == "BINANCE:trade:BTCUSDT:123456789"
    assert event["source"] == "binance"
    assert event["symbol"] == "BTCUSDT"
    assert event["trade_id"] == 123456789
    assert event["price"] == 63250.12
    assert event["quantity"] == 0.015
    assert event["stream"] == "trade"
