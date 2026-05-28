from datetime import UTC, datetime

from app.schemas.market import DashboardResponse, MarketItem


def testMarketItemNormalizesNonFiniteNumbersToNone():
    item = MarketItem.model_validate(
        {
            "name": "Test Index",
            "symbol": "TEST",
            "value": float("nan"),
            "change": float("inf"),
            "changePercent": "-Infinity",
            "currency": "USD",
            "marketStatus": "delayed",
            "asOf": datetime.now(UTC).isoformat(),
            "source": "test",
        }
    )

    assert item.value is None
    assert item.change is None
    assert item.changePercent is None


def testDashboardResponseValidatesNestedSections():
    response = DashboardResponse.model_validate(
        {
            "generatedAt": datetime.now(UTC).isoformat(),
            "sections": [
                {
                    "id": "sample",
                    "title": "Sample",
                    "items": [
                        {
                            "name": "Sample",
                            "symbol": "SMP",
                            "value": 100,
                            "change": 1.2,
                            "changePercent": 1.2,
                            "currency": "USD",
                            "marketStatus": "delayed",
                            "asOf": datetime.now(UTC).isoformat(),
                            "source": "test",
                        }
                    ],
                }
            ],
        }
    )

    assert response.sections[0].items[0].changePercent == 1.2
