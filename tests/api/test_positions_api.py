import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_positions(client: AsyncClient) -> None:
    payload = {
        "position_id": "p42",
        "owner_address": "0xowner",
        "collateral_symbol": "ETH",
        "collateral_amount": "1.2",
        "debt_symbol": "USDC",
        "debt_amount": "2000",
    }
    resp = await client.post("/positions/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["position_id"] == payload["position_id"]

    resp2 = await client.get("/positions/?limit=10")
    assert resp2.status_code == 200
    items = resp2.json()
    assert any(p["position_id"] == payload["position_id"] for p in items)
