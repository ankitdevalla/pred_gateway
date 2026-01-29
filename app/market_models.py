# app/market_models.py
from datetime import datetime
from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    market_id: str
    question: str
    implied_probability: float = Field(..., ge=0.0, le=1.0)
    close_time: datetime
    fetched_at: datetime
    status: str
    result: str | None = None
