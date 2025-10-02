from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.liquidation import (
    LiquidationExecuteRequest,
    LiquidationExecuteResponse,
    LiquidationSimulateResponse,
)
from app.services.liquidation import LiquidationService

router = APIRouter()


@router.get(
    "/simulate/{position_id}",
    response_model=LiquidationSimulateResponse,
    summary="Simulate Liquidation",
    description="""
    Simulate liquidation for a specific CDP position without executing it.
    
    This endpoint calculates:
    - Current health factor
    - Liquidation eligibility
    - Estimated profit from liquidation
    
    **Parameters:**
    - `position_id`: Unique identifier of the position to simulate
    
    **Returns:**
    - `position_id`: The position being simulated
    - `health_factor`: Current health factor (lower = more risky)
    - `eligible`: Whether the position is eligible for liquidation
    - `estimated_profit_usd`: Estimated profit in USD if liquidated
    
    **Health Factor Calculation:**
    ```
    health_factor = (collateral_usd * liquidation_threshold) / debt_usd
    ```
    
    Positions with health_factor < 1.0 are eligible for liquidation.
    
    **Example Response:**
    ```json
    {
        "position_id": "pos_001",
        "health_factor": 0.85,
        "eligible": true,
        "estimated_profit_usd": 1500.0
    }
    ```
    """,
    responses={
        200: {"description": "Simulation completed successfully"},
        400: {"description": "Invalid position ID or calculation error"},
        404: {"description": "Position not found"},
        500: {"description": "Internal server error"}
    }
)
async def simulate(
    position_id: str, session: AsyncSession = Depends(get_session)
) -> LiquidationSimulateResponse:
    """Simulate liquidation for a position."""
    if not position_id or not position_id.strip():
        raise HTTPException(status_code=400, detail="position_id cannot be empty")

    service = LiquidationService(session=session)
    try:
        return await service.simulate_liquidation(position_id=position_id.strip())
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post(
    "/execute",
    response_model=LiquidationExecuteResponse,
    summary="Execute Liquidation",
    description="""
    Execute liquidation for a CDP position that is eligible for liquidation.
    
    **Required Fields:**
    - `position_id`: Unique identifier of the position to liquidate
    - `max_slippage_bps`: Maximum acceptable slippage in basis points (0-10000)
    
    **Process:**
    1. Validates position exists and is eligible for liquidation
    2. Simulates the liquidation to ensure profitability
    3. Executes the liquidation transaction (simulated in demo)
    4. Returns transaction hash and realized profit
    
    **Slippage Protection:**
    - `max_slippage_bps` is the maximum acceptable price slippage
    - 100 bps = 1% slippage
    - 10000 bps = 100% slippage (maximum)
    
    **Example Request:**
    ```json
    {
        "position_id": "pos_001",
        "max_slippage_bps": 100
    }
    ```
    
    **Example Response:**
    ```json
    {
        "position_id": "pos_001",
        "tx_hash": "0x1234567890abcdef...",
        "realized_profit_usd": 1500.0
    }
    ```
    
    **Note:** In production, this would execute actual blockchain transactions.
    """,
    responses={
        200: {"description": "Liquidation executed successfully"},
        400: {"description": "Invalid parameters or position not eligible"},
        404: {"description": "Position not found"},
        500: {"description": "Internal server error"}
    }
)
async def execute(
    req: LiquidationExecuteRequest, session: AsyncSession = Depends(get_session)
) -> LiquidationExecuteResponse:
    """Execute liquidation for a position."""
    if not req.position_id or not req.position_id.strip():
        raise HTTPException(status_code=400, detail="position_id cannot be empty")

    service = LiquidationService(session=session)
    try:
        return await service.execute_liquidation(
            position_id=req.position_id.strip(), max_slippage_bps=req.max_slippage_bps
        )
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
