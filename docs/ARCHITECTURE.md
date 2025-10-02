### Architecture Overview

This backend provides multiple cohesive apps in one FastAPI project:

- Liquidation App
  - Services: `app/services/liquidation.py`
  - API: `app/api/routes/liquidation.py`
  - Uses: `PriceOracleClient`, `RiskEvaluator`, Postgres models

- Monitoring App
  - Services: `app/services/monitor.py`
  - API: `app/api/routes/monitor.py`
  - Periodic loop for contracts/logs, externally start/stop via API

- Analytics (planned)
  - Services: TBD (`app/services/analytics/...`)
  - API: TBD (`app/api/routes/analytics.py`)

#### Core
- Configuration via Pydantic Settings in `app/core/config.py`
- Structured logging (`app/core/logging.py`)
- Async DB (SQLAlchemy 2.0 + asyncpg) and Alembic

#### Data Model
- `Position` for demo purposes, stored in Postgres
- Future: events snapshots, risk metrics, liquidation history

#### Observability
- Structured logs; metrics endpoint can be added under `/metrics`

#### Testing Strategy
- Unit: services and utils
- API: endpoint tests via httpx with app factory
- DB: migrations in CI, integration tests on Postgres service

#### Deployment
- Dockerfile and `docker-compose.yml`
- CI runs lint, type checks, migrations, and tests
