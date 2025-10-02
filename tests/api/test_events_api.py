import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_events_index_and_list(client: AsyncClient) -> None:
    resp = await client.post("/events/index?from_block=1&to_block=3")
    assert resp.status_code == 200
    assert resp.json()["indexed"] == 3

    lst = await client.get("/events/?limit=10")
    assert lst.status_code == 200
    items = lst.json()
    assert len(items) >= 3
    assert all("block_number" in e for e in items)
