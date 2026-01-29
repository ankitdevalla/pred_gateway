import logging, uuid
from fastapi import FastAPI, Request
from datetime import datetime, date
from typing import Dict, Tuple

from app.logging import setup_logging, request_id_ctx_var
from app.models import ForecastRequest, ForecastResult, ConfidenceInterval

# in-memory idempotency store
FORECAST_STORE: Dict[Tuple[str, date], ForecastResult] = {}


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(name="prediction market LLM gateway")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_ctx_var.set(request_id)
    try:
        response = await call_next(request)
        return response
    finally:
        request_id_ctx_var.reset(token)

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


def generate_dummy_forecast(market_id: str, forecast_time: datetime) -> ForecastResult:
    """
    Deterministic, fake forecast.
    No randomness. No Kalshi. No LLM.
    """
    probability = 0.5
    ci = ConfidenceInterval(lower_bound=0.3, upper_bound=0.7)

    return ForecastResult(
        market_id=market_id,
        probability=probability,
        confidence_interval=ci,
        forecast_time=forecast_time,
    )

@app.post("/forecast", response_model=ForecastResult)
async def forecast(request: ForecastRequest):
    forecast_date = request.forecast_time.date()
    key = (request.market_id, forecast_date)

    # Idempotency check
    if key in FORECAST_STORE:
        logger.info(
            "Returning existing forecast",
            extra={"market_id": request.market_id, "date": forecast_date},
        )
        return FORECAST_STORE[key]

    # Generate deterministic dummy forecast
    result = generate_dummy_forecast(
        market_id=request.market_id,
        forecast_time=request.forecast_time,
    )

    # Store immutably
    FORECAST_STORE[key] = result

    logger.info(
        "Created new forecast",
        extra={
            "market_id": request.market_id,
            "probability": result.probability,
            "ci_low": result.confidence_interval.lower_bound,
            "ci_high": result.confidence_interval.upper_bound,
        },
    )

    return result
