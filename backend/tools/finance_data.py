import logging
from datetime import datetime, timedelta
from typing import TypedDict

import pandas as pd
import yfinance as yf
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Simple in-memory LRU cache to prevent rate-limiting from Yahoo Finance
# Caches up to 200 items for 1 hour (3600 seconds)
cache = TTLCache(maxsize=200, ttl=3600)

class PricePointDict(TypedDict):
    """Internal dictionary structure for price points in the tools layer."""
    date: str
    price: float

def get_historical_prices(ticker: str, days: int = 30) -> list[dict]:
    """
    Public entry point for fetching historical prices with caching.
    Ensures ticker normalisation and avoids caching negative (empty) results.
    """
    ticker = ticker.upper()
    cache_key = (ticker, days)
    
    if cache_key in cache:
        return cache[cache_key]

    result = _fetch_from_yfinance(ticker, days)
    
    # Only cache non-empty successful results to avoid locking in 
    # API failures or temporary unavailability for the full TTL.
    if result:
        cache[cache_key] = result
        
    return result

def _fetch_from_yfinance(ticker: str, days: int = 30) -> list[dict]:
    """
    Internal logic to fetch structured historical prices from Yahoo Finance.
    Takes into account weekends/holidays by fetching a broader range and limiting to `days`.
    """
    end_date = datetime.now()
    # Fetch extra days to account for non-trading days
    start_date = end_date - timedelta(days=days + 15)

    try:
        stock = yf.Ticker(ticker)
        df: pd.DataFrame = stock.history(
            start=start_date.strftime('%Y-%m-%d'), 
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if df is None or df.empty:
            return []

        prices: list[dict] = []
        
        # Take exactly the last `days` rows (or less if the stock hasn't traded that long)
        for date, row in df.tail(days).iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"])
            })
            
        return prices
    except Exception:
        # Avoid crashing if the API is down or the ticker is invalid.
        # logger.exception automatically includes the full stack trace.
        logger.exception("Error fetching historical data for %s", ticker)
        return []
