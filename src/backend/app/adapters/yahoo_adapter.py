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
    SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=12&newsCount=0"
    DETAIL_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range}"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    ALLOWED_RANGES = {
        "1D": {"range": "1d", "interval": "5m"},
        "1M": {"range": "1mo", "interval": "1d"},
        "3M": {"range": "3mo", "interval": "1d"},
        "1Y": {"range": "1y", "interval": "1d"},
    }
    US_EXCHANGES = {"ASE", "BATS", "NCM", "NGM", "NMS", "NYQ", "PCX", "PNK"}
    KR_EXCHANGES = {"KSC", "KOE", "KOS"}
    LOOKUP_CACHE_MAX_ITEMS = 128

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
        lookup_cache_max_items: int | None = None,
        max_workers: int = 8,
    ) -> None:
        self.fetch_url = fetch_url or urlopen
        self.timeout = timeout if timeout is not None else settings.yahoo_api_timeout
        self.cache_ttl_seconds = cache_ttl_seconds if cache_ttl_seconds is not None else settings.cache_ttl_seconds
        self.lookup_cache_max_items = (
            lookup_cache_max_items if lookup_cache_max_items is not None else self.LOOKUP_CACHE_MAX_ITEMS
        )
        self.max_workers = max_workers
        self._cache: dict[str, Any] | None = None
        self._cache_expires_at = 0.0
        self._lookup_cache: dict[str, tuple[float, dict[str, Any]]] = {}
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

    def search_symbols(self, query: str) -> dict[str, Any]:
        normalized_query = query.strip()
        cached = self._get_lookup_cache(f"search:{normalized_query.lower()}")
        if cached is not None:
            return cached

        request = Request(
            self.SEARCH_URL.format(query=quote(normalized_query, safe="")),
            headers={"User-Agent": self.USER_AGENT, "Accept": "application/json"},
        )
        try:
            with self.fetch_url(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise MarketDataProviderError("Yahoo Finance search request failed.") from exc

        results = []
        seen_symbols = set()
        for quote_item in payload.get("quotes") or []:
            parsed_item = self._parse_search_result(quote_item)
            if parsed_item is None or parsed_item["providerSymbol"] in seen_symbols:
                continue
            seen_symbols.add(parsed_item["providerSymbol"])
            results.append(parsed_item)

        data = {"query": normalized_query, "results": results}
        self._set_lookup_cache(f"search:{normalized_query.lower()}", data)
        return deepcopy(data)

    def get_stock_detail(self, symbol: str, range_str: str) -> dict[str, Any]:
        normalized_symbol = symbol.strip().upper()
        normalized_range = range_str.strip().upper()
        if normalized_range not in self.ALLOWED_RANGES:
            raise ValueError("Unsupported range.")

        cache_key = f"detail:{normalized_symbol}:{normalized_range}"
        cached = self._get_lookup_cache(cache_key)
        if cached is not None:
            return cached

        range_config = self.ALLOWED_RANGES[normalized_range]
        request = Request(
            self.DETAIL_URL.format(
                symbol=quote(normalized_symbol, safe=""),
                interval=range_config["interval"],
                range=range_config["range"],
            ),
            headers={"User-Agent": self.USER_AGENT, "Accept": "application/json"},
        )
        try:
            with self.fetch_url(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise MarketDataProviderError("Yahoo Finance chart request failed.") from exc

        data = self._parse_detail_payload(normalized_symbol, normalized_range, payload)
        self._set_lookup_cache(cache_key, data)
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

    def _get_lookup_cache(self, key: str) -> dict[str, Any] | None:
        with self._cache_lock:
            now = time.monotonic()
            cached = self._lookup_cache.get(key)
            if cached is not None and now < cached[0]:
                return deepcopy(cached[1])
            if cached is not None:
                self._lookup_cache.pop(key, None)
        return None

    def _set_lookup_cache(self, key: str, data: dict[str, Any]) -> None:
        with self._cache_lock:
            now = time.monotonic()
            self._prune_expired_lookup_cache(now)
            self._lookup_cache[key] = (now + self.cache_ttl_seconds, deepcopy(data))
            self._evict_lookup_cache()

    def _prune_expired_lookup_cache(self, now: float) -> None:
        expired_keys = [key for key, (expires_at, _) in self._lookup_cache.items() if now >= expires_at]
        for key in expired_keys:
            self._lookup_cache.pop(key, None)

    def _evict_lookup_cache(self) -> None:
        max_items = max(1, self.lookup_cache_max_items)
        while len(self._lookup_cache) > max_items:
            oldest_key = min(self._lookup_cache, key=lambda cache_key: self._lookup_cache[cache_key][0])
            self._lookup_cache.pop(oldest_key, None)

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

    def _parse_search_result(self, quote_item: dict[str, Any]) -> dict[str, Any] | None:
        symbol = quote_item.get("symbol")
        name = quote_item.get("shortname") or quote_item.get("longname") or quote_item.get("name")
        if not isinstance(symbol, str) or not symbol.strip() or not isinstance(name, str) or not name.strip():
            return None

        instrument_type = self._instrument_type(quote_item)
        country = self._country(quote_item, symbol)
        if instrument_type is None or country is None:
            return None

        exchange = str(quote_item.get("exchange") or quote_item.get("exchDisp") or "-")
        currency = str(quote_item.get("currency") or ("KRW" if country == "KR" else "USD"))
        provider_symbol = symbol.strip().upper()
        return {
            "symbol": self._display_symbol(provider_symbol),
            "displaySymbol": self._display_symbol(provider_symbol),
            "name": name.strip(),
            "exchange": exchange,
            "country": country,
            "instrumentType": instrument_type,
            "currency": currency,
            "providerSymbol": provider_symbol,
            "source": "yahoo-finance-search",
        }

    def _parse_detail_payload(self, symbol: str, range_str: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._chart_result(payload)
        meta = result.get("meta") or {}
        timestamps = result.get("timestamp") or []
        quote_data = ((result.get("indicators") or {}).get("quote") or [{}])[0] or {}
        currency = str(meta.get("currency") or ("KRW" if self._is_kr_symbol(symbol) else "USD"))
        instrument_type = self._meta_instrument_type(meta)
        country = self._detail_country(meta, symbol)
        if instrument_type is None or country is None:
            raise MarketDataProviderError("Yahoo Finance chart response is not a supported Korea/US stock or ETF.")
        price = self._finite(meta.get("regularMarketPrice"))
        previous_close = self._previous_close(meta)
        as_of = self._as_of(meta, datetime.now(UTC)).isoformat()
        instrument = {
            "symbol": self._display_symbol(symbol),
            "displaySymbol": self._display_symbol(symbol),
            "name": str(meta.get("longName") or meta.get("shortName") or symbol),
            "exchange": str(meta.get("exchangeName") or meta.get("fullExchangeName") or meta.get("exchange") or "-"),
            "country": country,
            "instrumentType": instrument_type,
            "currency": currency,
            "providerSymbol": symbol,
            "source": "yahoo-finance-v8",
        }
        data = {
            "instrument": instrument,
            "quote": {
                "price": price,
                "change": self._calculate_change(price, previous_close),
                "changePercent": self._calculate_change_percent(price, previous_close),
                "open": self._finite(meta.get("regularMarketOpen")),
                "high": self._finite(meta.get("regularMarketDayHigh")),
                "low": self._finite(meta.get("regularMarketDayLow")),
                "previousClose": self._finite(meta.get("chartPreviousClose")),
                "regularMarketPreviousClose": self._finite(meta.get("regularMarketPreviousClose") or meta.get("previousClose")),
                "volume": self._finite(meta.get("regularMarketVolume")),
                "currency": currency,
                "marketStatus": self._market_status(meta),
                "asOf": as_of,
                "source": "yahoo-finance-v8",
            },
            "chart": self._chart_points(timestamps, quote_data),
            "range": range_str,
        }
        if data["quote"]["price"] is None and not data["chart"]:
            raise MarketDataProviderError("Yahoo Finance chart response is missing usable stock data.")
        return data

    def _chart_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        error = payload.get("chart", {}).get("error")
        if error:
            raise MarketDataProviderError("Yahoo Finance chart response contains an error.")
        result = payload.get("chart", {}).get("result")
        if not result:
            raise MarketDataProviderError("Yahoo Finance chart response is missing result data.")
        return result[0]

    def _chart_points(self, timestamps: list[Any], quote_data: dict[str, Any]) -> list[dict[str, Any]]:
        fields = {
            "open": quote_data.get("open") or [],
            "high": quote_data.get("high") or [],
            "low": quote_data.get("low") or [],
            "close": quote_data.get("close") or [],
            "volume": quote_data.get("volume") or [],
        }
        points = []
        for index, timestamp in enumerate(timestamps):
            if not isinstance(timestamp, (int, float)) or not math.isfinite(timestamp):
                continue
            point = {"timestamp": datetime.fromtimestamp(timestamp, UTC).isoformat()}
            for field_name, values in fields.items():
                point[field_name] = self._finite(values[index]) if index < len(values) else None
            if any(point[field_name] is not None for field_name in fields):
                points.append(point)
        return points

    def _instrument_type(self, quote_item: dict[str, Any]) -> str | None:
        quote_type = str(quote_item.get("quoteType") or "").upper()
        type_disp = str(quote_item.get("typeDisp") or "").upper()
        if quote_type == "ETF" or type_disp == "ETF":
            return "etf"
        if quote_type == "EQUITY":
            return "stock"
        return None

    def _meta_instrument_type(self, meta: dict[str, Any]) -> str | None:
        instrument_type = str(meta.get("instrumentType") or "").upper()
        if instrument_type == "ETF":
            return "etf"
        if instrument_type in {"EQUITY", "STOCK"}:
            return "stock"
        return None

    def _country(self, quote_item: dict[str, Any], symbol: str) -> str | None:
        exchange = str(quote_item.get("exchange") or "").upper()
        if exchange in self.KR_EXCHANGES or self._is_kr_symbol(symbol):
            return "KR"
        if exchange in self.US_EXCHANGES:
            return "US"
        return None

    def _is_kr_symbol(self, symbol: str) -> bool:
        upper_symbol = symbol.upper()
        return upper_symbol.endswith(".KS") or upper_symbol.endswith(".KQ")

    def _detail_country(self, meta: dict[str, Any], symbol: str) -> str | None:
        exchange = str(meta.get("exchangeName") or meta.get("exchange") or "").upper()
        if exchange in self.KR_EXCHANGES or self._is_kr_symbol(symbol):
            return "KR"
        if exchange in self.US_EXCHANGES:
            return "US"
        if "." not in symbol:
            return "US"
        return None

    def _display_symbol(self, symbol: str) -> str:
        if self._is_kr_symbol(symbol):
            return symbol.rsplit(".", 1)[0]
        return symbol.upper()

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
