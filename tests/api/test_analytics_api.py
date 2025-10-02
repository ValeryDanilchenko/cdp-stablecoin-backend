import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_snapshot_and_list(client: AsyncClient) -> None:
    await client.post(
        "/positions/",
        json={
            "position_id": "pa1",
            "owner_address": "0xowner",
            "collateral_symbol": "ETH",
            "collateral_amount": "2.0",
            "debt_symbol": "USDC",
            "debt_amount": "1000",
        },
    )

    snap = await client.post("/analytics/snapshot/pa1")
    assert snap.status_code == 200
    data = snap.json()
    assert data["position_id"] == "pa1"
    assert "health_factor" in data

    lst = await client.get("/analytics/snapshots?limit=5")
    assert lst.status_code == 200
    items = lst.json()
    assert len(items) >= 1
