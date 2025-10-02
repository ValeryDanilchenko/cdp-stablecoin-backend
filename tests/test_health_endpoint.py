import httpx
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint_ok() -> None:
    app: FastAPI = create_app()
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
