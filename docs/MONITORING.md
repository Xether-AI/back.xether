# Monitoring & Optimization Guide

This guide describes how to monitor the health and performance of the Xether AI Backend and how to optimize it for scale.

## Observability Stack

The application natively supports **Prometheus** metrics and **Structured JSON Logging**.

### 1. Prometheus Metrics

The `/metrics` endpoint (protected or public depending on config) provides:

- `http_requests_total`: Total count of requests by method, path, and status.
- `http_request_duration_seconds`: Latency histograms.
- `sqlalchemy_pool_size`: Database connection pool status.
- `fastapi_app_info`: Metadata about the running version.

**Prometheus Config Snippet**:

```yaml
scrape_configs:
  - job_name: "xether-backend"
    scrape_interval: 15s
    static_configs:
      - targets: ["backend:8000"]
```

### 2. Grafana Dashboards

We recommend setting up a Grafana dashboard with the following panels:

- **Throughput**: `rate(http_requests_total[5m])`
- **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`
- **P95 Latency**: `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`

## Performance Optimization

### 1. Caching Strategy

- **Service Layer**: Use `@cache` decorator for expensive DB lookups (e.g., getting users by ID).
- **TTL Policies**: Default 10 minutes for metadata, 1 hour for static team info.
- **Invalidation**: Automatic invalidation is implemented in `user_service.update_user`.

### 2. Database Profiling

If endpoints are slow, enable SQL logging in `.env`:

```bash
LOG_LEVEL="DEBUG"
```

Check for "N+1" query patterns in logs.

### 3. Concurrency Tuning

Gunicorn workers can be adjusted based on CPU cores:

- **Formula**: `2 * cores + 1`.
- Update `Dockerfile` or `docker-compose.yml` to change `--workers 4`.

## Alerting Foundation

We recommend the following alerting rules in Prometheus Alertmanager:

- **ApiHighErrorRate**: Alert if 5xx errors > 1% for 5 minutes.
- **ApiHighLatency**: Alert if P95 latency > 500ms for 10 minutes.
- **DbConnectionSaturation**: Alert if pool usage > 90% for 5 minutes.
