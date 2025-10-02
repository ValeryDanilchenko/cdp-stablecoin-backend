import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liquidation_simulate_and_execute(client: AsyncClient) -> None:
    # create position
    await client.post(
        "/positions/",
        json={
            "position_id": "p100",
            "owner_address": "0xowner",
            "collateral_symbol": "ETH",
            "collateral_amount": "1.0",
            "debt_symbol": "USDC",
            "debt_amount": "1000",
        },
    )

    sim = await client.get("/liquidation/simulate/p100")
    assert sim.status_code == 200
    sim_data = sim.json()
    assert "health_factor" in sim_data

    exec_resp = await client.post("/liquidation/execute", json={"position_id": "p100", "max_slippage_bps": 100})
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert "tx_hash" in exec_data
