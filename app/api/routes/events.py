from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.chain_event import ChainEvent
from app.services.indexer import Web3Indexer

router = APIRouter(prefix="/events", tags=["events"]) 


@router.get("/", response_model=list[dict])
async def list_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    items = await Web3Indexer(session).list_events(limit=limit, offset=offset)
    return [
        {
            "id": e.id,
            "block_number": e.block_number,
            "tx_hash": e.tx_hash,
            "log_index": e.log_index,
            "event_name": e.event_name,
            "contract_address": e.contract_address,
            "data": e.data,
        }
        for e in items
    ]


@router.post("/index")
async def index_range(
    from_block: int = Query(..., ge=0),
    to_block: int = Query(..., ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    if to_block < from_block:
        raise HTTPException(status_code=400, detail="to_block must be >= from_block")
    count = await Web3Indexer(session).index_block_range(from_block=from_block, to_block=to_block)
    return {"indexed": count}
