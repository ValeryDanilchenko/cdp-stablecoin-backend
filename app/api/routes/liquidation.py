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
    service = LiquidationService(session=session)
    try:
        return await service.simulate_liquidation(position_id=position_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/execute", response_model=LiquidationExecuteResponse)
async def execute(
    req: LiquidationExecuteRequest, session: AsyncSession = Depends(get_session)
) -> LiquidationExecuteResponse:
    service = LiquidationService(session=session)
    return await service.execute_liquidation(
        position_id=req.position_id, max_slippage_bps=req.max_slippage_bps
    )
