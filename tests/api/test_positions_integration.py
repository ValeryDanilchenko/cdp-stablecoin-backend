"""Integration tests for positions API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position


@pytest.mark.asyncio
async def test_create_and_list_positions(client: AsyncClient, test_session: AsyncSession):
    """Test creating and listing positions."""
    import uuid
    # Test creating a position
    position_data = {
        "position_id": f"pos_{uuid.uuid4().hex[:8]}",
        "owner_address": "0x1234567890123456789012345678901234567890",
        "collateral_symbol": "ETH",
        "collateral_amount": "10.5",
        "debt_symbol": "USDC",
        "debt_amount": "25000.0",
    }
    
    response = await client.post("/positions/", json=position_data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    assert response.status_code == 201
    
    created_position = response.json()
    assert created_position["position_id"] == position_data["position_id"]
    assert created_position["owner_address"] == position_data["owner_address"]
    assert created_position["collateral_symbol"] == position_data["collateral_symbol"]
    assert created_position["collateral_amount"] == position_data["collateral_amount"]
    assert created_position["debt_symbol"] == position_data["debt_symbol"]
    assert created_position["debt_amount"] == position_data["debt_amount"]
    assert "id" in created_position
    assert "created_at" in created_position
    assert "updated_at" in created_position
    
    # Test listing positions
    response = await client.get("/positions/")
    assert response.status_code == 200
    
    positions = response.json()
    assert len(positions) == 1
    assert positions[0]["position_id"] == position_data["position_id"]


@pytest.mark.asyncio
async def test_create_duplicate_position_fails(client: AsyncClient, test_session: AsyncSession):
    """Test that creating a duplicate position fails."""
    position_data = {
        "position_id": "pos_duplicate",
        "owner_address": "0x1234567890123456789012345678901234567890",
        "collateral_symbol": "ETH",
        "collateral_amount": "10.5",
        "debt_symbol": "USDC",
        "debt_amount": "25000.0",
    }
    
    # Create first position
    response = await client.post("/positions/", json=position_data)
    assert response.status_code == 201
    
    # Try to create duplicate
    response = await client.post("/positions/", json=position_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_positions_with_pagination(client: AsyncClient, test_session: AsyncSession):
    """Test listing positions with pagination."""
    # Create multiple positions
    positions_data = [
        {
            "position_id": f"pos_{i:03d}",
            "owner_address": f"0x{i:040d}",
            "collateral_symbol": "ETH",
            "collateral_amount": "10.5",
            "debt_symbol": "USDC",
            "debt_amount": "25000.0",
        }
        for i in range(5)
    ]
    
    for position_data in positions_data:
        response = await client.post("/positions/", json=position_data)
        assert response.status_code == 201
    
    # Test pagination
    response = await client.get("/positions/?limit=2&offset=0")
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) == 2
    
    response = await client.get("/positions/?limit=2&offset=2")
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) == 2
    
    response = await client.get("/positions/?limit=2&offset=4")
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) == 1


@pytest.mark.asyncio
async def test_position_validation(client: AsyncClient, test_session: AsyncSession):
    """Test position data validation."""
    # Test missing required fields
    invalid_data = {
        "position_id": "pos_invalid",
        # Missing other required fields
    }
    
    response = await client.post("/positions/", json=invalid_data)
    assert response.status_code == 422  # Validation error
    
    # Test invalid pagination parameters
    response = await client.get("/positions/?limit=0")
    assert response.status_code == 422
    
    response = await client.get("/positions/?limit=101")
    assert response.status_code == 422
    
    response = await client.get("/positions/?offset=-1")
    assert response.status_code == 422
