import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_monitor_start_status_stop(client: AsyncClient) -> None:
    start = await client.post("/monitor/start")
    assert start.status_code in (200, 409)

    status = await client.get("/monitor/status")
    assert status.status_code == 200
    s = status.json()
    assert "running" in s

    stop = await client.post("/monitor/stop")
    assert stop.status_code == 200
