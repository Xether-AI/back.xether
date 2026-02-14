# Xether AI Backend - Setup Guide

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for local development)
- Git

### Local Development Setup

1. **Clone the repository** (if not already done)

   ```bash
   cd /home/polo/Documents/Xether\ AI/backend
   ```

2. **Create virtual environment**

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and set JWT_SECRET_KEY to a secure random value
   ```

5. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

6. **Start services with Docker Compose**

   ```bash
   docker-compose up -d postgres redis
   ```

7. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy app/
```

### Docker Development

To run the entire stack with Docker:

```bash
docker-compose up --build
```

This will start:

- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on port 8000

### Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints (V1 implemented)
│   ├── core/             # Core configuration and utilities
│   │   ├── config.py     # Settings management
│   │   ├── logging.py    # Logging configuration
│   │   └── security.py   # Security utilities
│   ├── db/               # Database configuration
│   │   ├── session.py    # SQLAlchemy session
│   │   └── redis.py      # Redis connection
│   ├── models/           # Database models (User, Team, Project, Dataset, Pipeline)
│   ├── schemas/          # Pydantic schemas with examples
│   ├── services/         # Business logic & Service layer
│   └── worker/           # Celery background tasks
├── tests/
│   ├── unit/             # Unit tests (Mocked)
│   ├── integration/      # Integration tests (Live DB/Redis)
│   └── conftest.py       # Test fixtures
├── migrations/           # Alembic migrations
├── main.py               # Application entry point
├── pyproject.toml        # Project metadata and dependencies
├── requirements.txt      # Python dependencies
├── Dockerfile            # Multi-stage production image
├── docker-compose.yml    # Development stack
└── .env.example          # Environment variables template
```

## Current Status

✅ **Phases 1-7 are complete.**
The system features a robust API with integrated Authentication, RBAC, Caching (Redis), Background Tasks (Celery), and comprehensive testing (76% coverage).

Next focus:

- **Phase 8/9**: Full documentation and Production deployment tuning.
- **Phase 10**: Post-launch monitoring and optimization.

See [docs/TASKS.md](docs/TASKS.md) for the detailed implementation roadmap.
