import random
from locust import HttpUser, task, between

class XetherUser(HttpUser):
    wait_time = between(1, 2)
    token = None

    def on_start(self):
        """Perform login to get token before running tasks."""
        # Note: In a real test, we would use unique users from a CSV
        # For this basic implementation, we use a test user
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@xether.ai",
                "password": "testpassword123"
            }
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            # Fallback for headless testing if seed data isn't fully ready
            self.token = "fake-token-scenarios"

    project_id = 1  # Default fallback

    @task(3)
    def list_datasets(self):
        """Simulate high frequency dataset listing."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get(f"/api/v1/datasets/?project_id={self.project_id}", headers=headers, name="/datasets/")

    @task(1)
    def list_projects(self):
        """Simulate project browsing and capture an ID."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/v1/projects/", headers=headers, name="/projects/")
        if response.status_code == 200:
            projects = response.json()
            if projects:
                self.project_id = projects[0]["id"]


    @task(1)
    def get_user_profile(self):
        """Simulate profile access."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/v1/users/me", headers=headers, name="/users/me")

