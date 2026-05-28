from fastapi.testclient import TestClient

import main
from main import app


def testMarketDashboardEndpointReturnsDashboardPayload():
    client = TestClient(app)

    response = client.get("/api/v1/market/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "generatedAt" in payload
    assert [section["id"] for section in payload["sections"]] == [
        "us-indexes",
        "kr-indexes",
        "global-indexes",
        "fx-rates",
    ]
    assert payload["sections"][3]["items"][2]["name"] == "JPY/KRW (100엔)"


def testHealthEndpointReturnsOk():
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def testMarketDashboardEndpointReturnsSafeErrorWhenAdapterFails(monkeypatch):
    class FailingMarketDataAdapter:
        def get_dashboard_data(self):
            raise RuntimeError("provider timeout")

    monkeypatch.setattr(main, "market_data_adapter", FailingMarketDataAdapter())
    client = TestClient(app)

    response = client.get("/api/v1/market/dashboard")

    assert response.status_code == 500
    assert response.json() == {"detail": "Market dashboard data is temporarily unavailable."}
