"""Integration tests for User, Team, and Project management."""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.core.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_user_management(client: AsyncClient):
    """Test user profile retrieval and update."""
    # 1. Register and login
    user_data = {"email": "user@example.com", "password": "password123"}
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    login_res = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get /me
    response = await client.get(f"{settings.api_v1_prefix}/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == user_data["email"]

    # 3. Update /me
    new_email = "newuser@example.com"
    response = await client.patch(
        f"{settings.api_v1_prefix}/users/me",
        json={"email": new_email},
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == new_email


@pytest.mark.asyncio
async def test_team_and_project_lifecycle(client: AsyncClient):
    """Test Team creation, Member management, and Project creation."""
    # 1. Login as admin (first user is usually admin if we make them so, 
    # but here we just use a fresh user)
    user_data = {"email": "admin@example.com", "password": "password123"}
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    login_res = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Team
    team_data = {"name": "Test Team", "description": "A test team"}
    response = await client.post(f"{settings.api_v1_prefix}/teams/", json=team_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    team_id = response.json()["id"]

    # 3. Create Project in Team
    project_data = {"name": "Test Project", "description": "A test project", "team_id": team_id}
    response = await client.post(f"{settings.api_v1_prefix}/projects/", json=project_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    project_id = response.json()["id"]

    # 4. List Projects
    response = await client.get(f"{settings.api_v1_prefix}/projects/?team_id={team_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == project_data["name"]
