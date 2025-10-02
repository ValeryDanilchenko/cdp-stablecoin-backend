FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml .
RUN poetry install --no-interaction --no-ansi --without dev

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
