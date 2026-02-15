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

    @task(3)
    def list_datasets(self):
        """Simulate high frequency dataset listing."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/v1/datasets/", headers=headers, name="/datasets/")

    @task(2)
    def get_health(self):
        """Simulate liveness/readiness checks."""
        self.client.get("/health/liveness", name="/health/liveness")

    @task(1)
    def list_projects(self):
        """Simulate project browsing."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/v1/projects/", headers=headers, name="/projects/")

    @task(1)
    def get_user_profile(self):
        """Simulate profile access."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/v1/users/me", headers=headers, name="/users/me")

