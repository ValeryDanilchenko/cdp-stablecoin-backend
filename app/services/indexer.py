from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chain_event import ChainEvent


class Web3Indexer:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_block_range(self, from_block: int, to_block: int) -> int:
        # Demo stub: create one fake event per block
        count = 0
        for block in range(from_block, to_block + 1):
            evt = ChainEvent(
                block_number=block,
                tx_hash=f"0x{block:064x}",
                log_index=0,
                event_name="DemoEvent",
                contract_address="0x0000000000000000000000000000000000000000",
                data=json.dumps({"note": "demo"}),
            )
            self.session.add(evt)
            count += 1
        await self.session.commit()
        return count

    async def list_events(self, limit: int = 50, offset: int = 0) -> Sequence[ChainEvent]:
        from sqlalchemy import select
        stmt = select(ChainEvent).order_by(ChainEvent.id.desc()).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
