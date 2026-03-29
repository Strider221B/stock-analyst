import pytest
from unittest.mock import patch

@pytest.fixture
def auth_headers(client):
    # Register and login to get auth headers
    client.post("/api/auth/register", json={
        "email": "market_user@example.com",
        "password": "Password123!"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "market_user@example.com",
        "password": "Password123!"
    })
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@patch("routers.marketdata_routes.get_historical_prices")
def test_fetch_historical_prices_success(mock_get_prices, client, auth_headers):
    # Mock the finance_data response
    mock_get_prices.return_value = [
        {"date": "2026-01-01", "price": 175.50},
        {"date": "2026-01-02", "price": 176.00}
    ]
    
    response = client.get("/api/marketdata/AAPL/history?days=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["date"] == "2026-01-01"
    assert data[0]["price"] == 175.50
    mock_get_prices.assert_called_once_with("AAPL", 2)

@patch("routers.marketdata_routes.get_historical_prices")
def test_fetch_historical_prices_not_found(mock_get_prices, client, auth_headers):
    mock_get_prices.return_value = []
    
    response = client.get("/api/marketdata/INVALIDTCK/history?days=30", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No historical data found for this ticker"

def test_fetch_historical_prices_unauthenticated(client):
    response = client.get("/api/marketdata/AAPL/history")
    assert response.status_code == 401
