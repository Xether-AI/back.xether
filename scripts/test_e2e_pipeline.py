#!/usr/bin/env python3
"""End-to-end test script for Pipeline execution flow."""

import asyncio
import sys
import json
from pathlib import Path
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings

settings = get_settings()
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}{settings.api_v1_prefix}"

async def test_e2e_pipeline():
    """Run E2E pipeline test."""
    print("=" * 60)
    print("End-to-End Pipeline Integration Test")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # 1. Login
        print("\n1. Logging in...")
        try:
            login_res = await client.post(
                f"{API_V1}/auth/login",
                data={"username": "test@xether.ai", "password": "testpassword123"}
            )
            login_res.raise_for_status()
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

        # 2. Create Team
        print("\n2. Creating Team...")
        team_res = await client.post(f"{API_V1}/teams/", json={"name": "E2E Test Team"}, headers=headers)
        team_res.raise_for_status()
        team_id = team_res.json()["id"]
        print(f"✅ Team created: ID={team_id}")

        # 3. Create Project
        print("\n3. Creating Project...")
        project_res = await client.post(
            f"{API_V1}/projects/", 
            json={"name": "E2E Pipeline Project", "team_id": team_id}, 
            headers=headers
        )
        project_res.raise_for_status()
        project_id = project_res.json()["id"]
        print(f"✅ Project created: ID={project_id}")

        # 4. Create Pipeline
        print("\n4. Creating Pipeline...")
        pipeline_data = {
            "name": "E2E Test Pipeline",
            "project_id": project_id,
            "config": {"input": "test.csv", "operations": ["clean", "normalize"]}
        }
        pipeline_res = await client.post(f"{API_V1}/pipelines/", json=pipeline_data, headers=headers)
        pipeline_res.raise_for_status()
        pipeline_id = pipeline_res.json()["id"]
        print(f"✅ Pipeline created: ID={pipeline_id}")

        # 5. Trigger Execution
        print("\n5. Triggering Execution...")
        exec_res = await client.post(f"{API_V1}/pipelines/{pipeline_id}/execute", headers=headers)
        exec_res.raise_for_status()
        execution_id = exec_res.json()["id"]
        print(f"✅ Execution triggered: ID={execution_id}")

        # 6. Poll for Completion
        print("\n6. Polling for completion (max 30s)...")
        for i in range(30):
            await asyncio.sleep(2)
            status_res = await client.get(f"{API_V1}/pipelines/{pipeline_id}/executions", headers=headers)
            status_res.raise_for_status()
            executions = status_res.json()
            
            # Find our execution
            execution = next((e for e in executions if e["id"] == execution_id), None)
            if not execution:
                print("⚠️ Execution not found in list")
                continue
            
            print(f"   Status: {execution['status']} (Iteration {i+1})")
            if execution["status"] == "completed":
                print("\n🎉 SUCCESS: Pipeline execution completed!")
                return True
            if execution["status"] == "failed":
                print(f"\n❌ FAILED: Pipeline execution failed with error: {execution.get('error_message')}")
                return False
        
        print("\n⌛ TIMEOUT: Pipeline execution did not complete in time.")
        return False

async def main():
    success = await test_e2e_pipeline()
    if success:
        print("\nEnd-to-End Integration Verified! 🚀")
        sys.exit(0)
    else:
        print("\nEnd-to-End Integration Failed. ⚠️")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
