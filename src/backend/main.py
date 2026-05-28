from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.mock_adapter import MockMarketDataAdapter
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

market_data_adapter = MockMarketDataAdapter()


@app.get("/api/v1/health")
def getHealth() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/market/dashboard", response_model=DashboardResponse)
def getMarketDashboard() -> DashboardResponse:
    dashboard_data = market_data_adapter.get_dashboard_data()
    return DashboardResponse.model_validate(dashboard_data)
