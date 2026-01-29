# You want three models: ForecastRequest, ForecastResult, ConfidenceInterval
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class ConfidenceInterval(BaseModel):
    lower_bound: float
    upper_bound: float 

class ForecastResult(BaseModel):
    market_id: str
    probability: float = Field(..., ge=0.0, le=1.0)
    confidence_interval: ConfidenceInterval
    forecast_time: datetime


class ForecastRequest(BaseModel):
    market_id: str = Field(..., description="Kalshi market ID")
    forecast_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the forecast is generated",
    )