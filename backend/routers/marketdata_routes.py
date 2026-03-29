from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import Annotated, List

from constants import APITags
from routers.dependencies import get_current_user
from db_components.models.user import User
from tools.finance_data import get_historical_prices, PricePoint

router = APIRouter(
    prefix="/api/marketdata",
    tags=[APITags.ANALYSIS],
)

@router.get("/{ticker}/history", response_model=List[PricePoint])
async def fetch_historical_prices(
    ticker: Annotated[str, Path(description="The ticker symbol to fetch history for.")],
    current_user: Annotated[User, Depends(get_current_user)],
    days: Annotated[int, Query(description="Number of trading days to fetch", ge=1, le=365)] = 30,
) -> List[PricePoint]:
    """Retrieve historical closing prices for a given ticker."""
    prices = get_historical_prices(ticker.upper(), days)
    if not prices:
        # Returning 404 if no data was found, since this could mean the ticker is invalid
        raise HTTPException(status_code=404, detail="No historical data found for this ticker")
    return prices
