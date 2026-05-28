from abc import ABC, abstractmethod
from typing import Any


class MarketDataAdapter(ABC):
    @abstractmethod
    def get_dashboard_data(self) -> dict[str, Any]:
        """Return dashboard-ready market data grouped by section."""
