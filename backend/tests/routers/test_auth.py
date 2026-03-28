import pytest

def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"
    assert "refresh_token" in response.cookies

def test_register_user_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_login_user(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies

def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpassword123!"
    })
    assert response.status_code == 401

def test_refresh_token(client):
    # Register and login to get refresh token cookie
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "Password123!"
    })
    
    # Store cookie and issue refresh call
    cookies = {"refresh_token": login_response.cookies.get("refresh_token")}
    
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    refresh_response = client.post("/api/auth/refresh", cookies=cookies, headers=headers)
    
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

def test_logout_user(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "Password123!"
    })
    
    cookies = {"refresh_token": login_response.cookies.get("refresh_token")}
    
    # Needs auth headers from login if logout checks token, but logout checks current_user usually.
    # We should add the access token header.
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    logout_response = client.post("/api/auth/logout", cookies=cookies, headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"

    # Refresh should fail now since token is revoked
    failed_refresh = client.post("/api/auth/refresh", cookies=cookies, headers=headers)
    assert failed_refresh.status_code == 401
