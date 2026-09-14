from cryptopulse.ingestion.coinbase_websocket import CoinbaseWebSocketProvider


def test_websocket_trade_message_normalizes_events() -> None:
    message = """{
      "channel": "market_trades",
      "events": [{"trades": [{"trade_id": "42", "product_id": "BTC-USD",
        "price": "42000.5", "size": "0.01", "time": "2024-01-01T00:00:00Z"}]}]
    }"""
    events = CoinbaseWebSocketProvider().events_from_message(message, "BTC-USD")
    assert len(events) == 1
    assert str(events[0].price) == "42000.5"
    assert events[0].source_sequence == "42"


def test_websocket_ignores_non_trade_messages() -> None:
    assert (
        CoinbaseWebSocketProvider().events_from_message('{"channel": "heartbeats"}', "BTC-USD")
        == []
    )
