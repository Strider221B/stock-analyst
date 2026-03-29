import pytest
import uuid

@pytest.fixture
def auth_headers(client):
    # Register and login to get auth headers
    client.post("/api/auth/register", json={
        "email": "portfolio_user@example.com",
        "password": "Password123!"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "portfolio_user@example.com",
        "password": "Password123!"
    })
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def test_create_portfolio(client, auth_headers):
    response = client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["message"] == "Portfolio created successfully"

def test_get_portfolios(client, auth_headers):
    # Create
    client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    
    response = client.get("/api/portfolios", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "My Tech Stocks"
    assert data[0]["account_type"] == "DOMESTIC"

def test_add_portfolio_item(client, auth_headers):
    # Create portfolio
    client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    portfolio_id = portfolios[0]["id"]
    
    # Add item
    response = client.post(f"/api/portfolios/{portfolio_id}/items", json={
        "ticker": "AAPL"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["message"] == "Ticker added successfully"
    
    # Check if added
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    assert len(portfolios[0]["items"]) == 1
    assert portfolios[0]["items"][0]["ticker"] == "AAPL"

def test_add_portfolio_item_duplicate(client, auth_headers):
    client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    portfolio_id = portfolios[0]["id"]
    
    client.post(f"/api/portfolios/{portfolio_id}/items", json={
        "ticker": "AAPL"
    }, headers=auth_headers)
    
    response = client.post(f"/api/portfolios/{portfolio_id}/items", json={
        "ticker": "aapl"
    }, headers=auth_headers)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()

def test_add_portfolio_item_not_found(client, auth_headers):
    fake_id = str(uuid.uuid4())
    response = client.post(f"/api/portfolios/{fake_id}/items", json={
        "ticker": "AAPL"
    }, headers=auth_headers)
    assert response.status_code == 404

def test_remove_portfolio_item(client, auth_headers):
    # Create portfolio and item
    client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    portfolio_id = portfolios[0]["id"]
    
    client.post(f"/api/portfolios/{portfolio_id}/items", json={
        "ticker": "AAPL"
    }, headers=auth_headers)
    
    # Remove item
    response = client.delete(f"/api/portfolios/{portfolio_id}/items/AAPL", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Ticker removed successfully"
    
    # Verify removed
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    assert len(portfolios[0]["items"]) == 0

def test_remove_portfolio_item_not_found(client, auth_headers):
    client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    }, headers=auth_headers)
    
    portfolios = client.get("/api/portfolios", headers=auth_headers).json()
    portfolio_id = portfolios[0]["id"]
    
    response = client.delete(f"/api/portfolios/{portfolio_id}/items/NONEXISTENT", headers=auth_headers)
    assert response.status_code == 404

def test_create_portfolio_unauthenticated(client):
    response = client.post("/api/portfolios", json={
        "name": "My Tech Stocks",
        "account_type": "DOMESTIC"
    })
    assert response.status_code == 401

def test_get_portfolios_unauthenticated(client):
    response = client.get("/api/portfolios")
    assert response.status_code == 401

def test_add_portfolio_item_unauthenticated(client):
    response = client.post(f"/api/portfolios/{uuid.uuid4()}/items", json={
        "ticker": "AAPL"
    })
    assert response.status_code == 401

def test_remove_portfolio_item_unauthenticated(client):
    response = client.delete(f"/api/portfolios/{uuid.uuid4()}/items/AAPL")
    assert response.status_code == 401
