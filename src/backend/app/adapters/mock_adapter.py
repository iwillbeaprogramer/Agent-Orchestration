from datetime import UTC, datetime, timedelta
import math
from typing import Any

from app.adapters.base import MarketDataAdapter


class MockMarketDataAdapter(MarketDataAdapter):
    def get_dashboard_data(self) -> dict[str, Any]:
        generated_at = datetime.now(UTC).isoformat()
        return {
            "generatedAt": generated_at,
            "sections": [
                self._build_section("us-indexes", "US indexes", self._us_items(), generated_at),
                self._build_section("kr-indexes", "Korea indexes", self._kr_items(), generated_at),
                self._build_section("global-indexes", "Global indexes", self._global_items(), generated_at),
                self._build_section("fx-rates", "FX rates", self._fx_items(), generated_at),
            ],
        }

    def search_symbols(self, query: str) -> dict[str, Any]:
        normalized_query = query.strip().upper()
        results = [
            item
            for item in self._search_items()
            if normalized_query in item["providerSymbol"] or normalized_query in item["name"].upper()
        ]
        return {"query": query.strip(), "results": results}

    def get_stock_detail(self, symbol: str, range_str: str) -> dict[str, Any]:
        normalized_symbol = symbol.strip().upper()
        instrument = next(
            (item for item in self._search_items() if item["providerSymbol"] == normalized_symbol),
            self._search_item(normalized_symbol, normalized_symbol, normalized_symbol, "NMS", "US", "stock", "USD"),
        )
        chart = self._chart_points(range_str)
        price = chart[-1]["close"]
        previous_close = chart[0]["close"]
        return {
            "instrument": instrument,
            "quote": {
                "price": price,
                "change": price - previous_close,
                "changePercent": ((price - previous_close) / previous_close) * 100,
                "open": chart[-1]["open"],
                "high": chart[-1]["high"],
                "low": chart[-1]["low"],
                "previousClose": previous_close,
                "regularMarketPreviousClose": previous_close,
                "volume": chart[-1]["volume"],
                "currency": instrument["currency"],
                "marketStatus": "regular",
                "asOf": datetime.now(UTC).isoformat(),
                "source": "mock-adapter",
            },
            "chart": chart,
            "range": range_str,
        }

    def _build_section(
        self,
        section_id: str,
        title: str,
        items: list[dict[str, Any]],
        generated_at: str,
    ) -> dict[str, Any]:
        return {
            "id": section_id,
            "title": title,
            "items": [self._with_common_fields(item, generated_at) for item in items],
        }

    def _with_common_fields(self, item: dict[str, Any], generated_at: str) -> dict[str, Any]:
        return {
            **item,
            "marketStatus": item.get("marketStatus", "delayed"),
            "asOf": generated_at,
            "source": "mock-adapter",
        }

    def _us_items(self) -> list[dict[str, Any]]:
        return [
            self._item("S&P 500", "SPX", 5321.41, 22.19, 0.42, "USD"),
            self._item("Nasdaq Composite", "IXIC", 16834.22, 104.33, 0.62, "USD"),
            self._item("Dow Jones Industrial Average", "DJI", 39086.15, -83.04, -0.21, "USD"),
            self._item("Russell 2000", "RUT", 2073.48, 11.42, 0.55, "USD"),
        ]

    def _kr_items(self) -> list[dict[str, Any]]:
        return [
            self._item("KOSPI", "KOSPI", 2735.83, 18.21, 0.67, "KRW"),
            self._item("KOSDAQ", "KOSDAQ", 845.55, -3.46, -0.41, "KRW"),
            self._item("KOSPI 200", "KOSPI200", 372.18, 2.04, 0.55, "KRW"),
        ]

    def _global_items(self) -> list[dict[str, Any]]:
        return [
            self._item("Nikkei 225", "N225", 38617.10, 121.73, 0.32, "JPY"),
            self._item("Shanghai Composite", "SSEC", 3121.46, -9.62, -0.31, "CNY"),
            self._item("Hang Seng", "HSI", 18418.72, 88.58, 0.48, "HKD"),
            self._item("Euro Stoxx 50", "STOXX50E", 5034.22, 19.46, 0.39, "EUR"),
            self._item("FTSE 100", "FTSE", 8317.59, -14.03, -0.17, "GBP"),
            self._item("DAX", "DAX", 18693.37, 74.16, 0.40, "EUR"),
        ]

    def _fx_items(self) -> list[dict[str, Any]]:
        return [
            self._item("USD/KRW", "USD/KRW", 1364.20, -2.30, -0.17, "KRW"),
            self._item("EUR/KRW", "EUR/KRW", 1484.65, 4.76, 0.32, "KRW"),
            self._item("JPY/KRW (100)", "JPY/KRW", 872.48, 1.35, 0.15, "KRW"),
            self._item("CNY/KRW", "CNY/KRW", 188.21, -0.18, -0.10, "KRW"),
            self._item("USD/JPY", "USD/JPY", 156.34, 0.21, 0.13, "JPY"),
        ]

    def _search_items(self) -> list[dict[str, str]]:
        return [
            self._search_item("QLD", "QLD", "ProShares Ultra QQQ", "PCX", "US", "etf", "USD"),
            self._search_item("AAPL", "AAPL", "Apple Inc.", "NMS", "US", "stock", "USD"),
            self._search_item("005930", "005930.KS", "Samsung Electronics Co., Ltd.", "KSC", "KR", "stock", "KRW"),
            self._search_item("069500", "069500.KS", "KODEX 200", "KSC", "KR", "etf", "KRW"),
        ]

    def _search_item(
        self,
        symbol: str,
        provider_symbol: str,
        name: str,
        exchange: str,
        country: str,
        instrument_type: str,
        currency: str,
    ) -> dict[str, str]:
        return {
            "symbol": symbol,
            "displaySymbol": symbol,
            "name": name,
            "exchange": exchange,
            "country": country,
            "instrumentType": instrument_type,
            "currency": currency,
            "providerSymbol": provider_symbol,
            "source": "mock-adapter",
        }

    def _chart_points(self, range_str: str) -> list[dict[str, Any]]:
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        point_count = 24 if range_str == "1D" else 30
        step = timedelta(hours=1) if range_str == "1D" else timedelta(days=1)
        start = now - (point_count - 1) * step
        chart = []
        for index in range(point_count):
            value = 100 + index * 0.8
            chart.append(
                {
                    "timestamp": (start + index * step).isoformat(),
                    "open": self._finite(value - 0.4),
                    "high": self._finite(value + 1.2),
                    "low": self._finite(value - 1.1),
                    "close": self._finite(value),
                    "volume": 1000000 + index * 1000,
                }
            )
        return chart

    def _item(
        self,
        name: str,
        symbol: str,
        value: float,
        change: float,
        change_percent: float,
        currency: str,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "symbol": symbol,
            "value": self._finite(value),
            "change": self._finite(change),
            "changePercent": self._finite(change_percent),
            "currency": currency,
        }

    def _finite(self, value: float) -> float | None:
        return value if math.isfinite(value) else None
