# Locust

Locust is a powerful tool for load testing any APIs which are RESTful APIs.

## Why do we need to use Locust?

- We can simulate a large number of users accessing the API.
- We can simulate a large number of requests to the API.
- We can simulate a large number of requests to the API with different patterns.
- How many users can the API handle?
- How many requests per second can the API handle?
- How much time does it take for the API to respond?

## Usage

- Integrated into the docker compose file
- Just change start command as below in `docker-compose.yml`

```yaml
# 10 workers for locust test which is ideal for testing and recommended
command: /app/docker/start.sh
# or
# only one worker for development, so this is not ideal test with locust
command: /app/docker/start_dev.sh
```
