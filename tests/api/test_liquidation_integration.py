"""Integration tests for liquidation API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_liquidation_simulate_and_execute(client: AsyncClient, test_session: AsyncSession):
    """Test liquidation simulation and execution flow."""
    # First create a position
    position_data = {
        "position_id": "pos_liquidate_001",
        "owner_address": "0x1234567890123456789012345678901234567890",
        "collateral_symbol": "ETH",
        "collateral_amount": "1.0",  # Low collateral amount
        "debt_symbol": "USDC",
        "debt_amount": "5000.0",  # High debt amount - should be liquidatable
    }

    # Create position
    response = await client.post("/positions/", json=position_data)
    assert response.status_code == 201

    # Test liquidation simulation
    response = await client.get("/liquidation/simulate/pos_liquidate_001")
    assert response.status_code == 200

    simulation = response.json()
    assert simulation["position_id"] == "pos_liquidate_001"
    assert "health_factor" in simulation
    assert "eligible" in simulation
    assert "estimated_profit_usd" in simulation

    # Test liquidation execution
    execution_data = {
        "position_id": "pos_liquidate_001",
        "max_slippage_bps": 100,  # 1% slippage
    }

    response = await client.post("/liquidation/execute", json=execution_data)
    assert response.status_code == 200

    execution = response.json()
    assert execution["position_id"] == "pos_liquidate_001"
    assert "tx_hash" in execution
    assert "realized_profit_usd" in execution


@pytest.mark.asyncio
async def test_liquidation_simulate_nonexistent_position(client: AsyncClient, test_session: AsyncSession):
    """Test liquidation simulation for non-existent position."""
    response = await client.get("/liquidation/simulate/nonexistent_pos")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_liquidation_execute_nonexistent_position(client: AsyncClient, test_session: AsyncSession):
    """Test liquidation execution for non-existent position."""
    execution_data = {
        "position_id": "nonexistent_pos",
        "max_slippage_bps": 100,
    }

    response = await client.post("/liquidation/execute", json=execution_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_liquidation_execute_validation(client: AsyncClient, test_session: AsyncSession):
    """Test liquidation execution validation."""
    # Test invalid slippage values
    execution_data = {
        "position_id": "pos_test",
        "max_slippage_bps": -1,  # Invalid negative slippage
    }

    response = await client.post("/liquidation/execute", json=execution_data)
    assert response.status_code == 422

    execution_data = {
        "position_id": "pos_test",
        "max_slippage_bps": 10001,  # Invalid high slippage (>100%)
    }

    response = await client.post("/liquidation/execute", json=execution_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_liquidation_with_safe_position(client: AsyncClient, test_session: AsyncSession):
    """Test liquidation with a safe position (not liquidatable)."""
    # Create a safe position with high collateral, low debt
    position_data = {
        "position_id": "pos_safe_001",
        "owner_address": "0x1234567890123456789012345678901234567890",
        "collateral_symbol": "ETH",
        "collateral_amount": "100.0",  # High collateral
        "debt_symbol": "USDC",
        "debt_amount": "1000.0",  # Low debt - should be safe
    }

    # Create position
    response = await client.post("/positions/", json=position_data)
    assert response.status_code == 201

    # Test liquidation simulation - should not be eligible
    response = await client.get("/liquidation/simulate/pos_safe_001")
    assert response.status_code == 200

    simulation = response.json()
    assert simulation["position_id"] == "pos_safe_001"
    assert simulation["eligible"] is False  # Should not be liquidatable
    assert simulation["estimated_profit_usd"] == 0.0

    # Test liquidation execution - should return empty result
    execution_data = {
        "position_id": "pos_safe_001",
        "max_slippage_bps": 100,
    }

    response = await client.post("/liquidation/execute", json=execution_data)
    assert response.status_code == 200

    execution = response.json()
    assert execution["position_id"] == "pos_safe_001"
    assert execution["tx_hash"] == ""  # No transaction
    assert execution["realized_profit_usd"] == 0.0
