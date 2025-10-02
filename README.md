## CDP Skill Demo Backend (FastAPI)

Production-grade FastAPI backend showcasing a liquidation service for a CDP-like system. Async Postgres, Alembic, tests, Docker, and CI.

### Stack
- FastAPI, Pydantic v2, Pydantic Settings
- SQLAlchemy 2.0 (async) + asyncpg, Alembic
- httpx, web3.py
- pytest, pytest-asyncio, coverage
- ruff, black, isort, mypy, flake8, pre-commit
- Docker, docker-compose, GitHub Actions

### Quickstart
1. Copy env and set values:
```bash
cp .env.example .env
```
2. Enable Poetry in-project .venv and install:
```bash
poetry config virtualenvs.in-project true
poetry install
source .venv/bin/activate
```
3. Migrate and run locally:
```bash
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

- Docs: `http://localhost:8000/docs`
- Health: `GET /health`

### Migrations
```bash
poetry run alembic revision -m "message"
poetry run alembic upgrade head
```

### Tests
```bash
poetry run pytest -q
```

### Branching
- main: stable
- develop: integration
- chore/infra: infra & tooling
- feat/liquidation-service: domain service work
- ci/setup: CI and checks

### Structure
```
app/
  api/
  clients/
  core/
  db/
  models/
  schemas/
  services/
  main.py
alembic/
.github/workflows/
```

### Apps
- Liquidation: endpoints and services under `app/services/liquidation.py` and `app/api/routes/liquidation.py`
- Monitoring: continuous contracts monitoring under `app/services/monitor.py` and API under `app/api/routes/monitor.py`
- Analytics: planned module for snapshots and KPIs

See `docs/ARCHITECTURE.md` for a high-level overview.
