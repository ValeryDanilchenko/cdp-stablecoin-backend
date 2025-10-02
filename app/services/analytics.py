from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_oracle import PriceOracleClient
from app.models.analytics import RiskSnapshot
from app.models.position import Position
from app.services.risk import RiskEvaluator


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.risk = RiskEvaluator()
        self.oracle = PriceOracleClient()

    async def snapshot_position(self, position_id: str) -> RiskSnapshot:
        pos = await self._load_position(position_id)
        collateral_price = await self.oracle.get_price_usd(pos.collateral_symbol)
        debt_price = await self.oracle.get_price_usd(pos.debt_symbol)
        collateral_usd = float(pos.collateral_amount) * collateral_price
        debt_usd = float(pos.debt_amount) * debt_price
        metrics = self.risk.compute_health(collateral_usd=collateral_usd, debt_usd=debt_usd)
        snap = RiskSnapshot(position_id=position_id, health_factor=metrics.health_factor, eligible=metrics.eligible)
        self.session.add(snap)
        await self.session.commit()
        await self.session.refresh(snap)
        return snap

    async def list_snapshots(self, limit: int = 20, offset: int = 0) -> list[RiskSnapshot]:
        stmt = select(RiskSnapshot).order_by(RiskSnapshot.id.desc()).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def _load_position(self, position_id: str) -> Position:
        stmt = select(Position).where(Position.position_id == position_id)
        res = await self.session.execute(stmt)
        pos = res.scalar_one_or_none()
        if pos is None:
            raise ValueError("position not found")
        return pos
