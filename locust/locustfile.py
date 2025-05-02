from locust import HttpUser, between, task


class ProcessManagementUser(HttpUser):
    wait_time = between(0.1, 5)  # Reduced wait time for higher throughput

    @task(1)
    def get_processes(self):
        self.client.get("/api/v1/processes")

    @task(3)
    def get_process(self):
        # Use a random process ID to distribute load
        self.client.get(f"/api/v1/processes/{1}")

    def on_start(self):
        # Any setup code that should run when a user starts
        pass
