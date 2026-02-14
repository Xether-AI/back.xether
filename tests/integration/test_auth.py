"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    """Test user registration and subsequent login."""
    user_data = {
        "email": "testauth@example.com",
        "password": "strongpassword123"
    }
    
    # 1. Register
    response = await client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json=user_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    
    # 2. Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data=login_data
    )
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_protected_route(client: AsyncClient):
    """Test accessing a protected route without token and with valid token."""
    # 1. Unauthenticated
    response = await client.get(f"{settings.api_v1_prefix}/api-keys/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 2. Authenticated
    user_data = {
        "email": "testprotected@example.com",
        "password": "strongpassword123"
    }
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    
    login_response = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    access_token = login_response.json()["access_token"]
    
    response = await client.get(
        f"{settings.api_v1_prefix}/api-keys/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_api_key_authentication(client: AsyncClient):
    """Test authentication via API Key."""
    user_data = {
        "email": "testapikey@example.com",
        "password": "strongpassword123"
    }
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    
    login_response = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    access_token = login_response.json()["access_token"]
    
    # 1. Create API Key
    key_name = "test-key"
    response = await client.post(
        f"{settings.api_v1_prefix}/api-keys/",
        json={"name": key_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    api_key_data = response.json()
    api_key = api_key_data["key"]
    
    # 2. Use API Key to access a protected route
    response = await client.get(
        f"{settings.api_v1_prefix}/api-keys/",
        headers={settings.api_key_header: api_key}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
