from app.adapters.mock_adapter import MockMarketDataAdapter


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
