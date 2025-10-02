## CDP Skill Demo Backend (FastAPI)

Production-grade FastAPI backend showcasing a liquidation service for a CDP-like system. Async Postgres, Alembic, tests, Docker, and CI.

### Stack
- FastAPI, Pydantic v2, Pydantic Settings
- SQLAlchemy 2.0 (async) + asyncpg, Alembic
- httpx, web3.py
- pytest, pytest-asyncio, coverage
- ruff, black, isort, mypy, pre-commit
- Docker, docker-compose, GitHub Actions

### Quickstart
1. Copy env and set values:
```bash
cp .env.example .env
```
2. Run with Docker:
```bash
docker compose up --build
```
3. Local (Poetry):
```bash
poetry install
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
