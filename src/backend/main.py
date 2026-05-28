import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.yahoo_adapter import YahooMarketDataAdapter
from app.config import settings
from app.schemas.market import DashboardResponse

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
