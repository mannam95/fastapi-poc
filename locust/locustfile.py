import random

from locust import HttpUser, between, task


class ProcessUser(HttpUser):
    wait_time = between(0, 0.1)
    # host = "http://localhost:8000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize instance variables for random samples
        self.create_departments = random.sample(range(1, 5), random.randint(1, 4))
        self.create_locations = random.sample(range(1, 5), random.randint(1, 4))
        self.create_resources = random.sample(range(1, 5), random.randint(1, 4))
        self.create_roles = random.sample(range(1, 5), random.randint(1, 4))

        self.update_departments = random.sample(range(1, 5), random.randint(1, 4))
        self.update_locations = random.sample(range(1, 5), random.randint(1, 4))
        self.update_resources = random.sample(range(1, 5), random.randint(1, 4))
        self.update_roles = random.sample(range(1, 5), random.randint(1, 4))

    @task(1)
    def create_process(self):
        body = {
            "title": "random_title",
            "description": "random_description",
            "created_by_id": 1,
            "department_ids": self.create_departments,
            "location_ids": self.create_locations,
            "resource_ids": self.create_resources,
            "role_ids": self.create_roles,
        }
        self.client.post("/api/v1/processes", json=body)

    # @task(2)
    # def update_process(self):
    #     body = {
    #         "title": "updated_title",
    #         "department_ids": self.update_departments,
    #         "location_ids": self.update_locations,
    #         "resource_ids": self.update_resources,
    #         "role_ids": self.update_roles,
    #     }
    #     self.client.put(f"/api/v1/processes/{1}", json=body)

    # @task(3)
    # def get_process(self):
    #     # Use a random process ID to distribute load
    #     self.client.get(f"/api/v1/processes/{1}")

    # @task(4)
    # def get_processes(self):
    #     self.client.get("/api/v1/processes")

    def on_start(self):
        # Any setup code that should run when a user starts
        pass
