from unittest.mock import patch, MagicMock
import pandas as pd
from tools.finance_data import get_historical_prices, cache

def test_get_historical_prices_success():
    # Clear cache before test
    cache.clear()
    
    mock_df = pd.DataFrame({
        "Close": [150.0, 155.0]
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))

    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = mock_df

        prices = get_historical_prices("AAPL", days=2)
        
        assert len(prices) == 2
        assert prices[0]["date"] == "2026-01-01"
        assert prices[0]["price"] == 150.0
        assert prices[1]["date"] == "2026-01-02"
        assert prices[1]["price"] == 155.0

def test_get_historical_prices_empty():
    cache.clear()
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame()

        prices = get_historical_prices("INVALID", days=2)
        assert prices == []

def test_get_historical_prices_exception():
    cache.clear()
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = mock_ticker.return_value
        mock_instance.history.side_effect = Exception("API Error")

        prices = get_historical_prices("ERR", days=2)
        assert prices == []
