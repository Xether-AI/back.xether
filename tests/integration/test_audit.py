"""Integration tests for Audit logs."""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings

from app.services import audit as audit_service

settings = get_settings()


@pytest.mark.asyncio
async def test_audit_logs(client: AsyncClient, db_session: AsyncSession):
    """Test Audit log retrieval for admins."""
    # 1. Register
    user_data = {"email": "admin@xether.ai", "password": "password123"}
    await client.post(f"{settings.api_v1_prefix}/auth/register", json=user_data)
    
    # Use the session fixture to make user superuser
    from app.services import user as user_service
    user = await user_service.get_user_by_email(db_session, user_data["email"])
    if user:
        user.is_superuser = True
        await db_session.commit()
    else:
        pytest.fail("User not found after registration")

    login_res = await client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add a dummy log via service
    await audit_service.create_audit_log(
        db_session, 
        user_id=user.id, 
        action="test_action", 
        resource_type="test_resource"
    )


    # 2. Get /audit
    response = await client.get(f"{settings.api_v1_prefix}/audit/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["action"] == "test_action"
