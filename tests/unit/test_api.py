from fastapi.testclient import TestClient

from cryptopulse.api.main import app, get_repository


class FakeRepository:
    def ping(self) -> bool:
        return True

    def latest_market_bar(self) -> dict[str, str]:
        return {"symbol": "BTC-USD"}

    def market_history(self, interval: str, limit: int, offset: int) -> list[dict[str, str]]:
        assert interval == "1 minute"
        assert (limit, offset) == (1, 0)
        return [{"symbol": "BTC-USD"}]


def client() -> TestClient:
    app.dependency_overrides[get_repository] = FakeRepository
    return TestClient(app)


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_history_validates_pagination() -> None:
    response = client().get("/market/history?limit=0")
    assert response.status_code == 422


def test_market_history_reads_curated_repository() -> None:
    response = client().get("/market/history?limit=1")
    assert response.status_code == 200
    assert response.json()["items"] == [{"symbol": "BTC-USD"}]


def test_metrics_are_exposed_for_prometheus() -> None:
    response = client().get("/metrics")
    assert response.status_code == 200
    assert "cryptopulse_api_requests_total" in response.text


def test_assistant_rejects_investment_advice() -> None:
    response = client().post("/assistant/query", json={"question": "Should I buy Bitcoin?"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "unsupported_assistant_question"


def test_assistant_browser_route_rejects_investment_advice() -> None:
    response = client().get("/assistant/query?question=Should%20I%20buy%20Bitcoin%3F")
    assert response.status_code == 422
