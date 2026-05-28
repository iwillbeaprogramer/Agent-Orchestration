from app.adapters.mock_adapter import MockMarketDataAdapter
from app.adapters.yahoo_adapter import MarketDataProviderError, YahooMarketDataAdapter


class FakeYahooResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload


def yahooPayload(price=100.0, previous_close=95.0, regular_market_time=1779926400, market_state="REGULAR"):
    return (
        b'{"chart":{"result":[{"meta":{'
        + f'"regularMarketPrice":{price},'.encode()
        + f'"previousClose":{previous_close},'.encode()
        + f'"regularMarketTime":{regular_market_time},'.encode()
        + f'"marketState":"{market_state}"'.encode()
        + b"}}]}}"
    )


def testMockAdapterReturnsExpectedSections():
    data = MockMarketDataAdapter().get_dashboard_data()

    section_ids = [section["id"] for section in data["sections"]]

    assert section_ids == ["us-indexes", "kr-indexes", "global-indexes", "fx-rates"]
    assert len(data["sections"][0]["items"]) == 4
    assert len(data["sections"][1]["items"]) == 3
    assert len(data["sections"][2]["items"]) == 6
    assert len(data["sections"][3]["items"]) == 5


def testMockAdapterIncludesRequiredItemFields():
    data = MockMarketDataAdapter().get_dashboard_data()
    first_item = data["sections"][0]["items"][0]

    assert {
        "name",
        "symbol",
        "value",
        "change",
        "changePercent",
        "currency",
        "marketStatus",
        "asOf",
        "source",
    }.issubset(first_item.keys())


def testYahooAdapterReturnsLatestDashboardDataFromChartApi():
    requested_urls = []

    def fetch_url(request, timeout):
        requested_urls.append(request.full_url)
        return FakeYahooResponse(yahooPayload())

    data = YahooMarketDataAdapter(fetch_url=fetch_url, cache_ttl_seconds=60).get_dashboard_data()
    first_item = data["sections"][0]["items"][0]
    jpy_item = data["sections"][3]["items"][2]

    assert len(requested_urls) == 18
    assert data["sections"][0]["id"] == "us-indexes"
    assert first_item["source"] == "yahoo-finance-v8"
    assert first_item["marketStatus"] == "regular"
    assert first_item["value"] == 100.0
    assert first_item["change"] == 5.0
    assert first_item["changePercent"] == 5.263157894736842
    assert first_item["asOf"].startswith("2026-05-28T")
    assert jpy_item["name"] == "JPY/KRW (100엔)"
    assert jpy_item["value"] == 10000.0
    assert jpy_item["change"] == 500.0


def testYahooAdapterCachesDashboardData():
    call_count = 0

    def fetch_url(request, timeout):
        nonlocal call_count
        call_count += 1
        return FakeYahooResponse(yahooPayload())

    adapter = YahooMarketDataAdapter(fetch_url=fetch_url, cache_ttl_seconds=60)

    first_data = adapter.get_dashboard_data()
    second_data = adapter.get_dashboard_data()
    second_data["sections"][0]["items"][0]["value"] = 1
    third_data = adapter.get_dashboard_data()

    assert call_count == 18
    assert first_data == third_data
    assert third_data["sections"][0]["items"][0]["value"] == 100.0


def testYahooAdapterMarksPartialFailuresUnavailable():
    def fetch_url(request, timeout):
        if "%5EGSPC" in request.full_url:
            raise TimeoutError("provider timeout")
        return FakeYahooResponse(yahooPayload())

    data = YahooMarketDataAdapter(fetch_url=fetch_url, cache_ttl_seconds=0).get_dashboard_data()
    first_item = data["sections"][0]["items"][0]
    second_item = data["sections"][0]["items"][1]

    assert first_item["value"] is None
    assert first_item["marketStatus"] == "unavailable"
    assert first_item["source"] == "yahoo-finance-v8:unavailable"
    assert second_item["value"] == 100.0


def testYahooAdapterMarksMalformedProviderValuesUnavailable():
    def fetch_url(request, timeout):
        if "%5EGSPC" in request.full_url:
            return FakeYahooResponse(b'{"chart":{"result":[{"meta":{"previousClose":95}}]}}')
        return FakeYahooResponse(yahooPayload())

    data = YahooMarketDataAdapter(fetch_url=fetch_url, cache_ttl_seconds=0).get_dashboard_data()
    first_item = data["sections"][0]["items"][0]

    assert first_item["value"] is None
    assert first_item["marketStatus"] == "unavailable"
    assert first_item["source"] == "yahoo-finance-v8:unavailable"


def testYahooAdapterRaisesWhenAllProviderValuesFail():
    def fetch_url(request, timeout):
        raise TimeoutError("provider timeout")

    adapter = YahooMarketDataAdapter(fetch_url=fetch_url, cache_ttl_seconds=0)

    try:
        adapter.get_dashboard_data()
    except MarketDataProviderError as exc:
        assert "usable market values" in str(exc)
    else:
        raise AssertionError("Expected MarketDataProviderError")
