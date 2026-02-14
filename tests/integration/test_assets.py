"""Integration tests for Datasets and Pipelines."""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.core.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_dataset_and_pipeline_lifecycle(client: AsyncClient):
    """Test Dataset registration, versioning, and Pipeline execution."""
    # 1. Login
    user_data = {"email": "dev@example.com", "password": "password123"}
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    login_res = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Team and Project
    team_res = await client.post(f"{settings.api_v1_prefix}/teams/", json={"name": "Dev Team"}, headers=headers)
    team_id = team_res.json()["id"]
    project_res = await client.post(
        f"{settings.api_v1_prefix}/projects/", 
        json={"name": "ML Project", "team_id": team_id}, 
        headers=headers
    )
    project_id = project_res.json()["id"]

    # 3. Register Dataset
    dataset_data = {
        "name": "Iris Dataset",
        "project_id": project_id,
        "storage_path": "s3://bucket/iris.csv",
        "meta_data": {"format": "csv"}
    }
    dataset_res = await client.post(f"{settings.api_v1_prefix}/datasets/", json=dataset_data, headers=headers)
    assert dataset_res.status_code == status.HTTP_201_CREATED
    dataset_id = dataset_res.json()["id"]

    # 4. Create Dataset Version
    version_data = {"version": "v1.0", "storage_path": "s3://bucket/v1.0/iris.csv"}
    version_res = await client.post(
        f"{settings.api_v1_prefix}/datasets/{dataset_id}/versions", 
        json=version_data, 
        headers=headers
    )
    assert version_res.status_code == status.HTTP_201_CREATED

    # 5. Create Pipeline
    pipeline_data = {
        "name": "Train Pipeline",
        "project_id": project_id,
        "config": {"epochs": 10}
    }
    pipeline_res = await client.post(f"{settings.api_v1_prefix}/pipelines/", json=pipeline_data, headers=headers)
    assert pipeline_res.status_code == status.HTTP_201_CREATED
    pipeline_id = pipeline_res.json()["id"]

    # 6. Trigger Execution
    exec_res = await client.post(f"{settings.api_v1_prefix}/pipelines/{pipeline_id}/execute", headers=headers)
    assert exec_res.status_code == status.HTTP_201_CREATED
    assert exec_res.json()["status"] == "pending"
