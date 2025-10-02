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


@router.get("/simulate/{position_id}", response_model=LiquidationSimulateResponse)
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


@router.post("/execute", response_model=LiquidationExecuteResponse)
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
