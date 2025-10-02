from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_oracle import PriceOracleClient
from app.models.position import Position
from app.schemas.liquidation import (
    LiquidationExecuteResponse,
    LiquidationSimulateResponse,
)
from app.services.risk import RiskEvaluator


class LiquidationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.oracle = PriceOracleClient()
        self.risk = RiskEvaluator()

    async def _load_position(self, position_id: str) -> Position:
        stmt = select(Position).where(Position.position_id == position_id)
        res = await self.session.execute(stmt)
        position = res.scalar_one_or_none()
        if position is None:
            raise ValueError("position not found")
        return position

    async def simulate_liquidation(self, position_id: str) -> LiquidationSimulateResponse:
        pos = await self._load_position(position_id)
        collateral_price = await self.oracle.get_price_usd(pos.collateral_symbol)
        debt_price = await self.oracle.get_price_usd(pos.debt_symbol)
        collateral_usd = float(pos.collateral_amount) * collateral_price
        debt_usd = float(pos.debt_amount) * debt_price
        metrics = self.risk.compute_health(collateral_usd=collateral_usd, debt_usd=debt_usd)
        est_profit = max(collateral_usd - debt_usd, 0.0) if metrics.eligible else 0.0
        return LiquidationSimulateResponse(
            position_id=position_id,
            health_factor=metrics.health_factor,
            eligible=metrics.eligible,
            estimated_profit_usd=est_profit,
        )

    async def execute_liquidation(
        self, position_id: str, max_slippage_bps: int
    ) -> LiquidationExecuteResponse:
        sim = await self.simulate_liquidation(position_id)
        if not sim.eligible:
            return LiquidationExecuteResponse(
                position_id=position_id, tx_hash="", realized_profit_usd=0.0
            )
        # Placeholder execution path - in real system would build and send tx via web3
        tx_hash = "0x" + (abs(hash(position_id)) % (10**16)).to_bytes(8, "big").hex()
        return LiquidationExecuteResponse(
            position_id=position_id,
            tx_hash=tx_hash,
            realized_profit_usd=sim.estimated_profit_usd or 0.0,
        )
