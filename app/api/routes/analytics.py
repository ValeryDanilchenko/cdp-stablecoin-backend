from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.analytics import RiskSnapshotRead
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"]) 


@router.post("/snapshot/{position_id}", response_model=RiskSnapshotRead)
async def create_snapshot(position_id: str, session: AsyncSession = Depends(get_session)) -> RiskSnapshotRead:
    service = AnalyticsService(session)
    try:
        snap = await service.snapshot_position(position_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RiskSnapshotRead.model_validate(snap, from_attributes=True)


@router.get("/snapshots", response_model=list[RiskSnapshotRead])
async def list_snapshots(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[RiskSnapshotRead]:
    service = AnalyticsService(session)
    snaps = await service.list_snapshots(limit=limit, offset=offset)
    return [RiskSnapshotRead.model_validate(s, from_attributes=True) for s in snaps]
