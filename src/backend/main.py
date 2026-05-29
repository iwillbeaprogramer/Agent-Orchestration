import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.yahoo_adapter import MarketDataProviderError
from app.adapters.yahoo_adapter import YahooMarketDataAdapter
from app.config import settings
from app.schemas.market import DashboardResponse, SearchResponse, StockDetailResponse

app = FastAPI(
    title="Market Dashboard API",
    version="0.1.0",
    description="Aggregated market index and FX dashboard data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

market_data_adapter = YahooMarketDataAdapter()
logger = logging.getLogger(__name__)


@app.get("/api/v1/health")
def getHealth() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/market/dashboard", response_model=DashboardResponse)
def getMarketDashboard() -> DashboardResponse:
    try:
        dashboard_data = market_data_adapter.get_dashboard_data()
        return DashboardResponse.model_validate(dashboard_data)
    except Exception as exc:
        logger.exception("Failed to load market dashboard data")
        raise HTTPException(status_code=500, detail="Market dashboard data is temporarily unavailable.") from exc


@app.get("/api/v1/market/search", response_model=SearchResponse)
def searchMarketSymbols(query: str) -> SearchResponse:
    normalized_query = query.strip()
    if not normalized_query:
        raise HTTPException(status_code=400, detail="Search query is required.")
    if len(normalized_query) > 50:
        raise HTTPException(status_code=400, detail="Search query must be 50 characters or fewer.")

    try:
        search_data = market_data_adapter.search_symbols(normalized_query)
        return SearchResponse.model_validate(search_data)
    except MarketDataProviderError as exc:
        logger.exception("Failed to search market symbols")
        raise HTTPException(status_code=502, detail="Market search data is temporarily unavailable.") from exc
    except Exception as exc:
        logger.exception("Unexpected market search failure")
        raise HTTPException(status_code=500, detail="Market search data is temporarily unavailable.") from exc


@app.get("/api/v1/market/detail", response_model=StockDetailResponse)
def getMarketDetail(symbol: str, range: str = "1M") -> StockDetailResponse:
    normalized_symbol = symbol.strip()
    normalized_range = range.strip().upper()
    if not normalized_symbol:
        raise HTTPException(status_code=400, detail="Symbol is required.")
    if len(normalized_symbol) > 64:
        raise HTTPException(status_code=400, detail="Symbol must be 64 characters or fewer.")
    if normalized_range not in {"1D", "1M", "3M", "1Y"}:
        raise HTTPException(status_code=400, detail="Range must be one of 1D, 1M, 3M, or 1Y.")

    try:
        detail_data = market_data_adapter.get_stock_detail(normalized_symbol, normalized_range)
        return StockDetailResponse.model_validate(detail_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid stock detail request.") from exc
    except MarketDataProviderError as exc:
        logger.exception("Failed to load market detail")
        raise HTTPException(status_code=502, detail="Market detail data is temporarily unavailable.") from exc
    except Exception as exc:
        logger.exception("Unexpected market detail failure")
        raise HTTPException(status_code=500, detail="Market detail data is temporarily unavailable.") from exc
