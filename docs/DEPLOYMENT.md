# Production Deployment Guide

This guide outlines the process for deploying the Xether AI Backend to a production environment.

## Prerequisites

- Docker & Docker Compose (Plugin v2+)
- SSL Certificate (or Nginx Proxy Manager / Cloudflare)
- SMTP Server (for notifications - optional)
- Sentry DSN (for error tracking - optional)

## Environment Setup

1. **Clone the repository**:

   ```bash
   git clone git@gitlab.com:xether.ai/back.xether.git
   cd back.xether
   ```

2. **Configure Secrets**:
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   > [!IMPORTANT]
   > Ensure `JWT_SECRET_KEY` is a strong, unique 32+ character string.
   > Update `DATABASE_URL` and `REDIS_URL` to point to production instances.

## Deployment Options

### 1. Docker Compose (Recommended for Small-Mid Scale)

We use a production-optimized `docker-compose.yml`.

```bash
# Build and start services in detached mode
docker compose -f docker-compose.yml up -d --build
```

### 2. Manual ASGI Setup

If running outside Docker:

```bash
source venv/bin/activate
gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4 main:app
```

## Post-Deployment Tasks

### 1. Database Migrations

Always run migrations after a new deployment:

```bash
docker compose exec backend alembic upgrade head
```

### 2. Security Audit

- Ensure port `5432` and `6379` are NOT exposed to the internet.
- Verify `CORS_ORIGINS` is restricted to your frontend domain.
- Check that `DEBUG` is set to `false`.

## Monitoring & Logs

- **Logs**: `docker compose logs -f backend`
- **Metrics**: Access `http://your-ip:8000/metrics` for Prometheus.
- **Health**: Access `http://your-ip:8000/health/liveness`.
