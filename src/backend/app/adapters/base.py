from abc import ABC, abstractmethod
from typing import Any


class MarketDataAdapter(ABC):
    @abstractmethod
    def get_dashboard_data(self) -> dict[str, Any]:
        """Return dashboard-ready market data grouped by section."""

    @abstractmethod
    def search_symbols(self, query: str) -> dict[str, Any]:
        """Return stock and ETF search results for the given query."""

    @abstractmethod
    def get_stock_detail(self, symbol: str, range_str: str) -> dict[str, Any]:
        """Return quote metadata and chart points for a stock or ETF."""
