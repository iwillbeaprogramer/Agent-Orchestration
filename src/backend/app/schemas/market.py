from datetime import datetime
import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalizeFiniteNumber(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
        return None
    if isinstance(value, (float, int)) and not math.isfinite(value):
        return None
    return value


class MarketItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    symbol: str
    value: float | None = None
    change: float | None = None
    changePercent: float | None = Field(default=None, description="Percent change, not ratio.")
    currency: str
    marketStatus: str = "delayed"
    asOf: datetime
    source: str

    @field_validator("value", "change", "changePercent", mode="before")
    @classmethod
    def validateFiniteNumber(cls, value: Any) -> Any:
        return normalizeFiniteNumber(value)


class DashboardSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    items: list[MarketItem]


class DashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generatedAt: datetime
    sections: list[DashboardSection]


class SearchResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    displaySymbol: str
    name: str
    exchange: str
    country: str
    instrumentType: str
    currency: str
    providerSymbol: str
    source: str


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    results: list[SearchResultItem]


class StockInstrumentInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    displaySymbol: str
    name: str
    exchange: str
    country: str
    instrumentType: str
    currency: str
    providerSymbol: str
    source: str


class StockQuote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: float | None = None
    change: float | None = None
    changePercent: float | None = Field(default=None, description="Percent change, not ratio.")
    open: float | None = None
    high: float | None = None
    low: float | None = None
    previousClose: float | None = None
    regularMarketPreviousClose: float | None = None
    volume: float | None = None
    currency: str
    marketStatus: str
    asOf: datetime
    source: str

    @field_validator(
        "price",
        "change",
        "changePercent",
        "open",
        "high",
        "low",
        "previousClose",
        "regularMarketPreviousClose",
        "volume",
        mode="before",
    )
    @classmethod
    def validateFiniteNumber(cls, value: Any) -> Any:
        return normalizeFiniteNumber(value)


class ChartPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def validateFiniteNumber(cls, value: Any) -> Any:
        return normalizeFiniteNumber(value)


class StockDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instrument: StockInstrumentInfo
    quote: StockQuote
    chart: list[ChartPoint]
    range: str
