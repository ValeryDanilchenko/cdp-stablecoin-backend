from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionRead

router = APIRouter(prefix="/positions", tags=["positions"]) 


@router.get("/", response_model=list[PositionRead])
async def list_positions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[PositionRead]:
    stmt = select(Position).order_by(Position.id).limit(limit).offset(offset)
    res = await session.execute(stmt)
    rows: Sequence[Position] = res.scalars().all()
    return [PositionRead.model_validate(p, from_attributes=True) for p in rows]


@router.post("/", response_model=PositionRead, status_code=201)
async def create_position(payload: PositionCreate, session: AsyncSession = Depends(get_session)) -> PositionRead:
    position = Position(
        position_id=payload.position_id,
        owner_address=payload.owner_address,
        collateral_symbol=payload.collateral_symbol,
        collateral_amount=payload.collateral_amount,
        debt_symbol=payload.debt_symbol,
        debt_amount=payload.debt_amount,
    )
    session.add(position)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="position_id already exists") from exc
    await session.refresh(position)
    return PositionRead.model_validate(position, from_attributes=True)
