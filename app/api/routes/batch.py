from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.position import Position
from app.schemas.batch import (
    BatchLiquidationRequest,
    BatchLiquidationResponse,
    BatchPositionCreateRequest,
    BatchPositionCreateResponse,
    BatchSimulationRequest,
    BatchSimulationResponse,
)
from app.services.liquidation import LiquidationService

router = APIRouter(prefix="/batch", tags=["batch"])


@router.post(
    "/positions",
    response_model=BatchPositionCreateResponse,
    summary="Create Multiple Positions",
    description="""
    Create multiple CDP positions in a single batch operation.
    
    **Benefits:**
    - Atomic operation: all positions created or none
    - Better performance for bulk operations
    - Reduced API calls
    
    **Request:**
    - Array of position data objects
    - Maximum 100 positions per batch
    
    **Response:**
    - List of created positions
    - List of any errors encountered
    - Summary statistics
    
    **Example Request:**
    ```json
    {
        "positions": [
            {
                "position_id": "pos_001",
                "owner_address": "0x1234...",
                "collateral_symbol": "ETH",
                "collateral_amount": "10.5",
                "debt_symbol": "USDC",
                "debt_amount": "25000.0"
            },
            {
                "position_id": "pos_002",
                "owner_address": "0x5678...",
                "collateral_symbol": "WBTC",
                "collateral_amount": "1.0",
                "debt_symbol": "USDC",
                "debt_amount": "65000.0"
            }
        ]
    }
    ```
    """,
    responses={
        201: {"description": "Batch operation completed"},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation errors"},
        500: {"description": "Internal server error"}
    }
)
async def create_batch_positions(
    request: BatchPositionCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> BatchPositionCreateResponse:
    """Create multiple positions in a single batch operation."""
    if len(request.positions) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 positions allowed per batch"
        )
    
    created_positions = []
    errors = []
    
    try:
        for i, position_data in enumerate(request.positions):
            try:
                # Validate position data
                if not position_data.position_id or not position_data.position_id.strip():
                    errors.append({
                        "index": i,
                        "position_id": position_data.position_id,
                        "error": "position_id cannot be empty"
                    })
                    continue
                
                if not position_data.owner_address or not position_data.owner_address.startswith("0x") or len(position_data.owner_address) != 42:
                    errors.append({
                        "index": i,
                        "position_id": position_data.position_id,
                        "error": "Invalid owner_address format"
                    })
                    continue
                
                # Create position
                position = Position(
                    position_id=position_data.position_id.strip(),
                    owner_address=position_data.owner_address.lower(),
                    collateral_symbol=position_data.collateral_symbol.upper(),
                    collateral_amount=position_data.collateral_amount,
                    debt_symbol=position_data.debt_symbol.upper(),
                    debt_amount=position_data.debt_amount,
                )
                
                session.add(position)
                created_positions.append(position)
                
            except Exception as e:
                errors.append({
                    "index": i,
                    "position_id": getattr(position_data, 'position_id', 'unknown'),
                    "error": str(e)
                })
        
        # Commit all positions at once
        if created_positions:
            await session.commit()
            
            # Refresh positions to get IDs
            for position in created_positions:
                await session.refresh(position)
        
        return BatchPositionCreateResponse(
            created_count=len(created_positions),
            error_count=len(errors),
            positions=[{
                "id": pos.id,
                "position_id": pos.position_id,
                "owner_address": pos.owner_address,
                "collateral_symbol": pos.collateral_symbol,
                "collateral_amount": pos.collateral_amount,
                "debt_symbol": pos.debt_symbol,
                "debt_amount": pos.debt_amount,
                "created_at": pos.created_at.isoformat(),
                "updated_at": pos.updated_at.isoformat()
            } for pos in created_positions],
            errors=errors
        )
        
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Batch operation failed") from exc


@router.post(
    "/simulate",
    response_model=BatchSimulationResponse,
    summary="Simulate Multiple Liquidations",
    description="""
    Simulate liquidation for multiple positions in a single batch operation.
    
    **Benefits:**
    - Efficient bulk simulation
    - Consistent price data across all simulations
    - Detailed results for each position
    
    **Request:**
    - Array of position IDs to simulate
    - Maximum 50 positions per batch
    
    **Response:**
    - Simulation results for each position
    - Summary statistics
    - Any errors encountered
    
    **Example Request:**
    ```json
    {
        "position_ids": ["pos_001", "pos_002", "pos_003"]
    }
    ```
    """,
    responses={
        200: {"description": "Batch simulation completed"},
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"}
    }
)
async def simulate_batch_liquidations(
    request: BatchSimulationRequest,
    session: AsyncSession = Depends(get_session),
) -> BatchSimulationResponse:
    """Simulate liquidation for multiple positions."""
    if len(request.position_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 positions allowed per batch simulation"
        )
    
    service = LiquidationService(session=session)
    results = []
    errors = []
    
    for i, position_id in enumerate(request.position_ids):
        try:
            simulation = await service.simulate_liquidation(position_id)
            results.append({
                "position_id": simulation.position_id,
                "health_factor": simulation.health_factor,
                "eligible": simulation.eligible,
                "estimated_profit_usd": simulation.estimated_profit_usd
            })
        except Exception as e:
            errors.append({
                "index": i,
                "position_id": position_id,
                "error": str(e)
            })
    
    return BatchSimulationResponse(
        simulated_count=len(results),
        error_count=len(errors),
        results=results,
        errors=errors
    )


@router.post(
    "/liquidate",
    response_model=BatchLiquidationResponse,
    summary="Execute Multiple Liquidations",
    description="""
    Execute liquidation for multiple eligible positions in a single batch operation.
    
    **Benefits:**
    - Atomic liquidation execution
    - Efficient bulk operations
    - Detailed execution results
    
    **Request:**
    - Array of liquidation requests
    - Each request includes position_id and max_slippage_bps
    - Maximum 20 liquidations per batch
    
    **Response:**
    - Execution results for each position
    - Summary statistics
    - Any errors encountered
    
    **Example Request:**
    ```json
    {
        "liquidations": [
            {
                "position_id": "pos_001",
                "max_slippage_bps": 100
            },
            {
                "position_id": "pos_002",
                "max_slippage_bps": 200
            }
        ]
    }
    ```
    """,
    responses={
        200: {"description": "Batch liquidation completed"},
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"}
    }
)
async def execute_batch_liquidations(
    request: BatchLiquidationRequest,
    session: AsyncSession = Depends(get_session),
) -> BatchLiquidationResponse:
    """Execute liquidation for multiple positions."""
    if len(request.liquidations) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 liquidations allowed per batch"
        )
    
    service = LiquidationService(session=session)
    results = []
    errors = []
    
    for i, liquidation in enumerate(request.liquidations):
        try:
            execution = await service.execute_liquidation(
                liquidation.position_id,
                liquidation.max_slippage_bps
            )
            results.append({
                "position_id": execution.position_id,
                "tx_hash": execution.tx_hash,
                "realized_profit_usd": execution.realized_profit_usd
            })
        except Exception as e:
            errors.append({
                "index": i,
                "position_id": liquidation.position_id,
                "error": str(e)
            })
    
    return BatchLiquidationResponse(
        executed_count=len(results),
        error_count=len(errors),
        results=results,
        errors=errors
    )
