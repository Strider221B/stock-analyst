from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from typing import TypedDict, List
from cachetools import TTLCache, cached

# Simple in-memory LRU cache to prevent rate-limiting from Yahoo Finance
# Caches up to 200 items for 1 hour (3600 seconds)
cache = TTLCache(maxsize=200, ttl=3600)

class PricePoint(TypedDict):
    date: str
    price: float

@cached(cache)
def get_historical_prices(ticker: str, days: int = 30) -> List[PricePoint]:
    """
    Fetch structured historical closing prices for the last `days` from Yahoo Finance.
    Takes into account weekends/holidays by fetching a broader range and limiting to `days`.
    """
    end_date = datetime.now()
    # Fetch extra days to account for non-trading days
    start_date = end_date - timedelta(days=days + 15)

    stock = yf.Ticker(ticker)
    
    try:
        df: pd.DataFrame = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        if df is None or df.empty:
            return []

        prices: List[PricePoint] = []
        
        # Take exactly the last `days` rows (or less if the stock hasn't traded that long)
        for date, row in df.tail(days).iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"])
            })
            
        return prices
    except Exception as e:
        # Avoid crashing if the API is down or the ticker is invalid
        print(f"Error fetching historical data for {ticker}: {e}")
        return []
