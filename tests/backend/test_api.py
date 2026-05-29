from fastapi.testclient import TestClient

import main
from main import app


def testMarketDashboardEndpointReturnsDashboardPayload(monkeypatch):
    class StubMarketDataAdapter:
        def get_dashboard_data(self):
            return {
                "generatedAt": "2026-05-28T00:00:00+00:00",
                "sections": [
                    {
                        "id": "us-indexes",
                        "title": "미국 대표지수",
                        "items": [
                            {
                                "name": "S&P 500",
                                "symbol": "SPX",
                                "value": 100,
                                "change": 1,
                                "changePercent": 1,
                                "currency": "USD",
                                "marketStatus": "regular",
                                "asOf": "2026-05-28T00:00:00+00:00",
                                "source": "test",
                            }
                        ],
                    },
                    {"id": "kr-indexes", "title": "한국 대표지수", "items": []},
                    {"id": "global-indexes", "title": "기타국 대표지수", "items": []},
                    {
                        "id": "fx-rates",
                        "title": "환율",
                        "items": [
                            {
                                "name": "USD/KRW",
                                "symbol": "USD/KRW",
                                "value": 1364,
                                "change": 1,
                                "changePercent": 0.1,
                                "currency": "KRW",
                                "marketStatus": "regular",
                                "asOf": "2026-05-28T00:00:00+00:00",
                                "source": "test",
                            },
                            {
                                "name": "EUR/KRW",
                                "symbol": "EUR/KRW",
                                "value": 1484,
                                "change": 1,
                                "changePercent": 0.1,
                                "currency": "KRW",
                                "marketStatus": "regular",
                                "asOf": "2026-05-28T00:00:00+00:00",
                                "source": "test",
                            },
                            {
                                "name": "JPY/KRW (100엔)",
                                "symbol": "JPY/KRW",
                                "value": 940,
                                "change": 1,
                                "changePercent": 0.1,
                                "currency": "KRW",
                                "marketStatus": "regular",
                                "asOf": "2026-05-28T00:00:00+00:00",
                                "source": "test",
                            },
                        ],
                    },
                ],
            }

    monkeypatch.setattr(main, "market_data_adapter", StubMarketDataAdapter())
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


def testMarketSearchEndpointReturnsFilteredPayload(monkeypatch):
    class StubMarketDataAdapter:
        def search_symbols(self, query):
            return {
                "query": query,
                "results": [
                    {
                        "symbol": "QLD",
                        "displaySymbol": "QLD",
                        "name": "ProShares Ultra QQQ",
                        "exchange": "PCX",
                        "country": "US",
                        "instrumentType": "etf",
                        "currency": "USD",
                        "providerSymbol": "QLD",
                        "source": "test",
                    }
                ],
            }

    monkeypatch.setattr(main, "market_data_adapter", StubMarketDataAdapter())
    client = TestClient(app)

    response = client.get("/api/v1/market/search", params={"query": " qld "})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "qld"
    assert payload["results"][0]["providerSymbol"] == "QLD"


def testMarketSearchEndpointValidatesInput():
    client = TestClient(app)

    empty_response = client.get("/api/v1/market/search", params={"query": "   "})
    long_response = client.get("/api/v1/market/search", params={"query": "x" * 51})

    assert empty_response.status_code == 400
    assert long_response.status_code == 400


def testMarketDetailEndpointReturnsStockDetail(monkeypatch):
    class StubMarketDataAdapter:
        def get_stock_detail(self, symbol, range_str):
            return {
                "instrument": {
                    "symbol": symbol,
                    "displaySymbol": symbol,
                    "name": "ProShares Ultra QQQ",
                    "exchange": "PCX",
                    "country": "US",
                    "instrumentType": "etf",
                    "currency": "USD",
                    "providerSymbol": symbol,
                    "source": "test",
                },
                "quote": {
                    "price": 101.5,
                    "change": 1.5,
                    "changePercent": 1.5,
                    "open": 99.5,
                    "high": 102,
                    "low": 98.7,
                    "previousClose": 100,
                    "regularMarketPreviousClose": 100,
                    "volume": 1234,
                    "currency": "USD",
                    "marketStatus": "regular",
                    "asOf": "2026-05-28T00:00:00+00:00",
                    "source": "test",
                },
                "chart": [
                    {
                        "timestamp": "2026-05-28T00:00:00+00:00",
                        "open": 100,
                        "high": 102,
                        "low": 99,
                        "close": 101.5,
                        "volume": 1234,
                    }
                ],
                "range": range_str,
            }

    monkeypatch.setattr(main, "market_data_adapter", StubMarketDataAdapter())
    client = TestClient(app)

    response = client.get("/api/v1/market/detail", params={"symbol": "QLD", "range": "1M"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["instrument"]["providerSymbol"] == "QLD"
    assert payload["quote"]["changePercent"] == 1.5
    assert payload["range"] == "1M"


def testMarketDetailEndpointValidatesRange():
    client = TestClient(app)

    response = client.get("/api/v1/market/detail", params={"symbol": "QLD", "range": "5Y"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Range must be one of 1D, 1M, 3M, or 1Y."}
