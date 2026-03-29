from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from apis.marketdata_schemas import PricePoint
from constants import APITags
from db_components.models.user import User
from routers.dependencies import get_current_user
from tools.finance_data import get_historical_prices

router = APIRouter(
    prefix="/api/marketdata",
    tags=[APITags.MARKETDATA],
)

@router.get("/{ticker}/history", response_model=list[PricePoint])
async def fetch_historical_prices(
    ticker: Annotated[str, Path(description="The ticker symbol to fetch history for.")],
    current_user: Annotated[User, Depends(get_current_user)],
    days: Annotated[int, Query(description="Number of trading days to fetch", ge=1, le=365)] = 30,
) -> list[PricePoint]:
    """Retrieve historical closing prices for a given ticker."""
    prices = get_historical_prices(ticker, days)
    if not prices:
        # Returning 404 if no data was found, since this could mean the ticker is invalid
        raise HTTPException(status_code=404, detail="No historical data found for this ticker")
    return prices
