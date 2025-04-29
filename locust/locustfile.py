from locust import HttpUser, between, task

BASE_URL = "/api/v1"


class FastAPIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_data(self):
        self.client.get(f"{BASE_URL}/processes/")
