# Prometheus

Prometheus is a powerful tool for monitoring and alerting.

## Why do we need to use Prometheus?

### Why not Locust?

- The simulations we generated with Locust gives us some metrics such as:
  - How many requests per second can the API handle?
  - What is the response time of the API?
  - Failure rate of the API?

**My Opinion:**

- Locust is not a tool for monitoring and alerting. It is a tool for load testing.
- While some metrics are useful, we need more metrics to understand the performance of the API.
- We need a tool for monitoring and alerting.

### Now, let's see why Prometheus?

- Prometheus is a powerful tool for monitoring and alerting.
- It is like a wrapper to our application.
- Which can collect the metrics from our application and store them in a time series database
- The metrics includes:
  - Locust Metrics
  - CPU usage
  - Memory usage
  - Network usage
  - Disk usage
  - etc.

### What can we do with Prometheus?

- There is another tool called Grafana which can visualize the metrics.
- We can create dashboards and make the source of data from Prometheus.
- We can set alerts in Prometheus to notify us when the metrics are not good.

## Current Status

- Prometheus and Grafana are setup in our docker compose file.(But commented out.)
- The metrics are being collected by Prometheus. (Tested with Locust)
- I should create some cool dashboards to visualize the metrics. (TODO)
