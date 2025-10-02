from collections.abc import Sequence

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
async def create_position(
    payload: PositionCreate, session: AsyncSession = Depends(get_session)
) -> PositionRead:
    """Create a new position with comprehensive validation."""
    # Validate position_id format
    if not payload.position_id or not payload.position_id.strip():
        raise HTTPException(status_code=400, detail="position_id cannot be empty")

    # Validate owner_address format (basic Ethereum address check)
    if not payload.owner_address or not payload.owner_address.startswith("0x") or len(payload.owner_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid owner_address format")

    # Validate amounts are positive numbers
    try:
        collateral_amount = float(payload.collateral_amount)
        debt_amount = float(payload.debt_amount)
        if collateral_amount <= 0 or debt_amount <= 0:
            raise HTTPException(status_code=400, detail="Amounts must be positive")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid amount format")

    # Validate symbols are not empty
    if not payload.collateral_symbol.strip() or not payload.debt_symbol.strip():
        raise HTTPException(status_code=400, detail="Symbols cannot be empty")

    position = Position(
        position_id=payload.position_id.strip(),
        owner_address=payload.owner_address.lower(),
        collateral_symbol=payload.collateral_symbol.upper(),
        collateral_amount=payload.collateral_amount,
        debt_symbol=payload.debt_symbol.upper(),
        debt_amount=payload.debt_amount,
    )

    session.add(position)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="position_id already exists") from exc
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create position") from exc

    await session.refresh(position)
    return PositionRead.model_validate(position, from_attributes=True)
