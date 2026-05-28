from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import UTC, datetime
import json
import math
import threading
import time
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.adapters.base import MarketDataAdapter
from app.config import settings


FetchUrl = Callable[[Request, float], Any]


class MarketDataProviderError(RuntimeError):
    """Raised when the market data provider cannot return a usable dashboard."""


class YahooMarketDataAdapter(MarketDataAdapter):
    API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )

    SECTION_DEFINITIONS = [
        (
            "us-indexes",
            "미국 대표지수",
            [
                {"name": "S&P 500", "symbol": "SPX", "yahooSymbol": "^GSPC", "currency": "USD"},
                {"name": "Nasdaq Composite", "symbol": "IXIC", "yahooSymbol": "^IXIC", "currency": "USD"},
                {"name": "Dow Jones Industrial Average", "symbol": "DJI", "yahooSymbol": "^DJI", "currency": "USD"},
                {"name": "Russell 2000", "symbol": "RUT", "yahooSymbol": "^RUT", "currency": "USD"},
            ],
        ),
        (
            "kr-indexes",
            "한국 대표지수",
            [
                {"name": "KOSPI", "symbol": "KOSPI", "yahooSymbol": "^KS11", "currency": "KRW"},
                {"name": "KOSDAQ", "symbol": "KOSDAQ", "yahooSymbol": "^KQ11", "currency": "KRW"},
                {"name": "KOSPI 200", "symbol": "KOSPI200", "yahooSymbol": "^KS200", "currency": "KRW"},
            ],
        ),
        (
            "global-indexes",
            "기타국 대표지수",
            [
                {"name": "Nikkei 225", "symbol": "N225", "yahooSymbol": "^N225", "currency": "JPY"},
                {"name": "Shanghai Composite", "symbol": "SSEC", "yahooSymbol": "000001.SS", "currency": "CNY"},
                {"name": "Hang Seng", "symbol": "HSI", "yahooSymbol": "^HSI", "currency": "HKD"},
                {"name": "Euro Stoxx 50", "symbol": "STOXX50E", "yahooSymbol": "^STOXX50E", "currency": "EUR"},
                {"name": "FTSE 100", "symbol": "FTSE", "yahooSymbol": "^FTSE", "currency": "GBP"},
                {"name": "DAX", "symbol": "DAX", "yahooSymbol": "^GDAXI", "currency": "EUR"},
            ],
        ),
        (
            "fx-rates",
            "환율",
            [
                {"name": "USD/KRW", "symbol": "USD/KRW", "yahooSymbol": "USDKRW=X", "currency": "KRW"},
                {"name": "EUR/KRW", "symbol": "EUR/KRW", "yahooSymbol": "EURKRW=X", "currency": "KRW"},
                {
                    "name": "JPY/KRW (100엔)",
                    "symbol": "JPY/KRW",
                    "yahooSymbol": "JPYKRW=X",
                    "currency": "KRW",
                    "scale": 100,
                },
                {"name": "CNY/KRW", "symbol": "CNY/KRW", "yahooSymbol": "CNYKRW=X", "currency": "KRW"},
                {"name": "USD/JPY", "symbol": "USD/JPY", "yahooSymbol": "JPY=X", "currency": "JPY"},
            ],
        ),
    ]

    def __init__(
        self,
        *,
        fetch_url: FetchUrl | None = None,
        timeout: float | None = None,
        cache_ttl_seconds: int | None = None,
        max_workers: int = 8,
    ) -> None:
        self.fetch_url = fetch_url or urlopen
        self.timeout = timeout if timeout is not None else settings.yahoo_api_timeout
        self.cache_ttl_seconds = cache_ttl_seconds if cache_ttl_seconds is not None else settings.cache_ttl_seconds
        self.max_workers = max_workers
        self._cache: dict[str, Any] | None = None
        self._cache_expires_at = 0.0
        self._cache_lock = threading.Lock()

    def get_dashboard_data(self) -> dict[str, Any]:
        cached = self._get_cached_data()
        if cached is not None:
            return cached

        fetched_at = datetime.now(UTC)
        item_results = self._fetch_items(fetched_at)
        if not any(item["value"] is not None for item in item_results.values()):
            raise MarketDataProviderError("Yahoo Finance did not return any usable market values.")

        data = {
            "generatedAt": fetched_at.isoformat(),
            "sections": [
                self._build_section(section_id, title, items, item_results)
                for section_id, title, items in self.SECTION_DEFINITIONS
            ],
        }
        self._set_cached_data(data)
        return deepcopy(data)

    def _get_cached_data(self) -> dict[str, Any] | None:
        with self._cache_lock:
            if self._cache is not None and time.monotonic() < self._cache_expires_at:
                return deepcopy(self._cache)
        return None

    def _set_cached_data(self, data: dict[str, Any]) -> None:
        with self._cache_lock:
            self._cache = deepcopy(data)
            self._cache_expires_at = time.monotonic() + self.cache_ttl_seconds

    def _fetch_items(self, fetched_at: datetime) -> dict[str, dict[str, Any]]:
        item_configs = [item for _, _, items in self.SECTION_DEFINITIONS for item in items]
        max_workers = min(self.max_workers, len(item_configs))
        results: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(self._fetch_item, item, fetched_at): item for item in item_configs}
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    results[item["symbol"]] = future.result()
                except Exception:
                    results[item["symbol"]] = self._unavailable_item(item, fetched_at)
        return results

    def _fetch_item(self, item: dict[str, Any], fetched_at: datetime) -> dict[str, Any]:
        request = Request(
            self.API_URL.format(symbol=quote(item["yahooSymbol"], safe="")),
            headers={"User-Agent": self.USER_AGENT, "Accept": "application/json"},
        )
        with self.fetch_url(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return self._parse_item_payload(item, payload, fetched_at)

    def _parse_item_payload(self, item: dict[str, Any], payload: dict[str, Any], fetched_at: datetime) -> dict[str, Any]:
        meta = self._extract_meta(payload)
        price = self._scale_value(self._finite(meta.get("regularMarketPrice")), item)
        if price is None:
            raise MarketDataProviderError("Yahoo Finance chart response is missing a usable latest price.")
        previous_close = self._scale_value(self._previous_close(meta), item)
        change = self._calculate_change(price, previous_close)
        change_percent = self._calculate_change_percent(price, previous_close)
        return {
            "name": item["name"],
            "symbol": item["symbol"],
            "value": price,
            "change": change,
            "changePercent": change_percent,
            "currency": item["currency"],
            "marketStatus": self._market_status(meta),
            "asOf": self._as_of(meta, fetched_at).isoformat(),
            "source": "yahoo-finance-v8",
        }

    def _extract_meta(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = payload.get("chart", {}).get("result")
        if not result:
            raise MarketDataProviderError("Yahoo Finance chart response is missing result data.")
        return result[0].get("meta") or {}

    def _previous_close(self, meta: dict[str, Any]) -> float | None:
        for key in ("previousClose", "chartPreviousClose", "regularMarketPreviousClose"):
            value = self._finite(meta.get(key))
            if value is not None:
                return value
        return None

    def _unavailable_item(self, item: dict[str, Any], fetched_at: datetime) -> dict[str, Any]:
        return {
            "name": item["name"],
            "symbol": item["symbol"],
            "value": None,
            "change": None,
            "changePercent": None,
            "currency": item["currency"],
            "marketStatus": "unavailable",
            "asOf": fetched_at.isoformat(),
            "source": "yahoo-finance-v8:unavailable",
        }

    def _build_section(
        self,
        section_id: str,
        title: str,
        items: list[dict[str, Any]],
        item_results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "id": section_id,
            "title": title,
            "items": [item_results[item["symbol"]] for item in items],
        }

    def _scale_value(self, value: float | None, item: dict[str, Any]) -> float | None:
        if value is None:
            return None
        return self._finite(value * item.get("scale", 1))

    def _calculate_change(self, price: float | None, previous_close: float | None) -> float | None:
        if price is None or previous_close is None:
            return None
        return self._finite(price - previous_close)

    def _calculate_change_percent(self, price: float | None, previous_close: float | None) -> float | None:
        if price is None or previous_close in (None, 0):
            return None
        return self._finite(((price - previous_close) / previous_close) * 100)

    def _market_status(self, meta: dict[str, Any]) -> str:
        market_state = meta.get("marketState")
        if isinstance(market_state, str) and market_state.strip():
            return market_state.lower()
        return "delayed"

    def _as_of(self, meta: dict[str, Any], fetched_at: datetime) -> datetime:
        market_time = meta.get("regularMarketTime")
        if isinstance(market_time, (float, int)) and math.isfinite(market_time):
            return datetime.fromtimestamp(market_time, UTC)
        return fetched_at

    def _finite(self, value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (float, int)) and math.isfinite(value):
            return float(value)
        return None
