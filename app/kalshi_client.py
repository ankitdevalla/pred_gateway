import os
import requests
from datetime import datetime, timezone
from app.market_models import MarketSnapshot
from dotenv import load_dotenv
load_dotenv()

KALSHI_BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")
if not KALSHI_API_KEY:
    raise RuntimeError("KALSHI_API_KEY not set")

HEADERS = {
    "Authorization": f"Bearer {KALSHI_API_KEY}",
    "Content-Type": "application/json",
}

def _derive_implied_probability(market: dict) -> float:
    """
    Priority:
    1. Midpoint of yes bid/ask
    2. last_price
    3. yes_ask
    Prices are in cents.
    """
    yes_bid = market.get("yes_bid")
    yes_ask = market.get("yes_ask")
    last_price = market.get("last_price")

    if yes_bid is not None and yes_ask is not None:
        return ((yes_bid + yes_ask) / 2) / 100.0

    if last_price is not None:
        return last_price / 100.0

    raise ValueError("No usable price found to derive implied probability")


def fetch_market_snapshot(market_id: str) -> MarketSnapshot:
    url = f"{KALSHI_BASE_URL}/markets/{market_id}"

    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    market = resp.json()["market"]

    if market["market_type"] != "binary":
        raise ValueError(f"Unsupported market type: {market['market_type']}")

    implied_prob = _derive_implied_probability(market)

    close_time = datetime.fromisoformat(
        market["close_time"].replace("Z", "+00:00")
    )

    return MarketSnapshot(
        market_id=market["ticker"],
        question=market["title"],
        implied_probability=implied_prob,
        close_time=close_time,
        fetched_at=datetime.now(timezone.utc),
        status=market["status"],
        result=market.get("result"),
    )
