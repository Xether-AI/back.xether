"""Integration tests for RBAC Permission Matrix."""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.core.config import get_settings

settings = get_settings()

async def get_token_for_user(client: AsyncClient, email: str, password: str = "password123"):
    """Helper to register and get token for a user."""
    await client.post(f"{settings.api_v1_prefix}/auth/register", json={"email": email, "password": password})
    login_res = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": email, "password": password}
    )
    return login_res.json()["access_token"]

@pytest.mark.asyncio
async def test_rbac_project_access_matrix(client: AsyncClient):
    """
    Test permission matrix for projects:
    Roles: admin, manager, developer, viewer
    Actions: create_project, update_project, delete_project, list_projects
    """
    # 1. Setup Admin (Owner)
    admin_token = await get_token_for_user(client, "team_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Create Team
    team_res = await client.post(f"{settings.api_v1_prefix}/teams/", json={"name": "RBAC Team"}, headers=admin_headers)
    team_id = team_res.json()["id"]
    
    # 3. Setup other users
    roles = ["manager", "developer", "viewer"]
    user_tokens = {}
    for role in roles:
        email = f"{role}@example.com"
        token = await get_token_for_user(client, email)
        user_tokens[role] = token
        # Add to team with role
        await client.post(
            f"{settings.api_v1_prefix}/teams/{team_id}/members",
            json={"user_id": (await client.get(f"{settings.api_v1_prefix}/users/me", headers={"Authorization": f"Bearer {token}"})).json()["id"], "role": role},
            headers=admin_headers
        )

    # 4. Define Matrix
    # Format: (role, method, endpoint_suffix, expected_status)
    matrix = [
        # Project Creation (Admin & Manager only)
        ("admin", "POST", "/projects/", status.HTTP_201_CREATED, {"name": "P1", "team_id": team_id}),
        ("manager", "POST", "/projects/", status.HTTP_201_CREATED, {"name": "P2", "team_id": team_id}),
        ("developer", "POST", "/projects/", status.HTTP_403_FORBIDDEN, {"name": "P3", "team_id": team_id}),
        ("viewer", "POST", "/projects/", status.HTTP_403_FORBIDDEN, {"name": "P4", "team_id": team_id}),
    ]
    
    for role, method, suffix, expected_status, json_data in matrix:
        token = admin_token if role == "admin" else user_tokens[role]
        headers = {"Authorization": f"Bearer {token}"}
        
        if method == "POST":
            res = await client.post(f"{settings.api_v1_prefix}{suffix}", json=json_data, headers=headers)
        
        assert res.status_code == expected_status, f"Role {role} failed on {method} {suffix}. Expected {expected_status}, got {res.status_code}"

@pytest.mark.asyncio
async def test_rbac_project_modification_matrix(client: AsyncClient):
    """Test update/delete permissions."""
    # Setup
    admin_token = await get_token_for_user(client, "mod_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    team_res = await client.post(f"{settings.api_v1_prefix}/teams/", json={"name": "Mod Team"}, headers=admin_headers)
    team_id = team_res.json()["id"]
    
    proj_res = await client.post(f"{settings.api_v1_prefix}/projects/", json={"name": "Mod Proj", "team_id": team_id}, headers=admin_headers)
    project_id = proj_res.json()["id"]
    
    # Add a developer
    dev_token = await get_token_for_user(client, "mod_dev@example.com")
    dev_id = (await client.get(f"{settings.api_v1_prefix}/users/me", headers={"Authorization": f"Bearer {dev_token}"})).json()["id"]
    await client.post(f"{settings.api_v1_prefix}/teams/{team_id}/members", json={"user_id": dev_id, "role": "developer"}, headers=admin_headers)
    
    # Developer tries to delete project
    res = await client.delete(f"{settings.api_v1_prefix}/projects/{project_id}", headers={"Authorization": f"Bearer {dev_token}"})
    assert res.status_code == status.HTTP_403_FORBIDDEN
    
    # Admin deletes project
    res = await client.delete(f"{settings.api_v1_prefix}/projects/{project_id}", headers=admin_headers)
    assert res.status_code == status.HTTP_204_NO_CONTENT
