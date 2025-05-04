import random

from locust import HttpUser, between, task


class ProcessUser(HttpUser):
    # Simulates user "think time" between requests.
    wait_time = between(0.1, 2)
    # host = "http://localhost:8000"

    @task(1)
    def create_process(self):
        random_choices = random.choices(range(1, 61), k=5)
        body = {
            "title": "random_title",
            "description": "random_description",
            "created_by_id": 1,
            "department_ids": random_choices,
            "location_ids": random_choices,
            "resource_ids": random_choices,
            "role_ids": random_choices,
        }
        self.client.post("/api/v1/processes", json=body)

    @task(2)
    def update_process(self):
        random_choices = random.choices(range(1, 61), k=5)
        body = {
            "title": "updated_title",
            "department_ids": random_choices,
            "location_ids": random_choices,
            "resource_ids": random_choices,
            "role_ids": random_choices,
        }
        self.client.put(f"/api/v1/processes/{random.randint(1, 60)}", json=body)

    @task(3)
    def get_process(self):
        # Use a random process ID to distribute load
        self.client.get(f"/api/v1/processes/{1}")

    @task(4)
    def get_processes(self):
        self.client.get("/api/v1/processes")

    def on_start(self):
        # Any setup code that should run when a user starts
        pass
