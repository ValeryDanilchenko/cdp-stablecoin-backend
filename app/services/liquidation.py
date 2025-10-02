from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_oracle import PriceOracleClient
from app.models.position import Position
from app.schemas.liquidation import (
    LiquidationExecuteResponse,
    LiquidationSimulateResponse,
)
from app.services.risk import RiskEvaluator

logger = logging.getLogger("app.services.liquidation")


class LiquidationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.oracle = PriceOracleClient()
        self.risk = RiskEvaluator()

    async def _load_position(self, position_id: str) -> Position:
        """Load position by ID with proper error handling."""
        if not position_id or not position_id.strip():
            raise ValueError("position_id cannot be empty")
        
        stmt = select(Position).where(Position.position_id == position_id)
        res = await self.session.execute(stmt)
        position = res.scalar_one_or_none()
        if position is None:
            raise ValueError(f"Position with ID '{position_id}' not found")
        return position

    async def simulate_liquidation(self, position_id: str) -> LiquidationSimulateResponse:
        """Simulate liquidation with comprehensive error handling."""
        logger.info("Starting liquidation simulation", extra={
            "extra_fields": {"position_id": position_id}
        })
        
        try:
            pos = await self._load_position(position_id)
            logger.debug("Position loaded successfully", extra={
                "extra_fields": {
                    "position_id": position_id,
                    "collateral_symbol": pos.collateral_symbol,
                    "debt_symbol": pos.debt_symbol
                }
            })
        except ValueError as e:
            logger.error("Failed to load position", extra={
                "extra_fields": {"position_id": position_id, "error": str(e)}
            })
            raise ValueError(f"Failed to load position: {e}") from e
        
        try:
            collateral_price = await self.oracle.get_price_usd(pos.collateral_symbol)
            debt_price = await self.oracle.get_price_usd(pos.debt_symbol)
            logger.debug("Prices fetched successfully", extra={
                "extra_fields": {
                    "collateral_price": collateral_price,
                    "debt_price": debt_price
                }
            })
        except ValueError as e:
            logger.error("Price oracle error", extra={
                "extra_fields": {"position_id": position_id, "error": str(e)}
            })
            raise ValueError(f"Price oracle error: {e}") from e
        
        try:
            collateral_usd = float(pos.collateral_amount) * collateral_price
            debt_usd = float(pos.debt_amount) * debt_price
        except (ValueError, TypeError) as e:
            logger.error("Invalid amount format", extra={
                "extra_fields": {
                    "position_id": position_id,
                    "collateral_amount": pos.collateral_amount,
                    "debt_amount": pos.debt_amount,
                    "error": str(e)
                }
            })
            raise ValueError(f"Invalid amount format: {e}") from e
        
        if collateral_usd < 0 or debt_usd < 0:
            logger.error("Negative amounts detected", extra={
                "extra_fields": {
                    "position_id": position_id,
                    "collateral_usd": collateral_usd,
                    "debt_usd": debt_usd
                }
            })
            raise ValueError("Amounts cannot be negative")
        
        metrics = self.risk.compute_health(collateral_usd=collateral_usd, debt_usd=debt_usd)
        est_profit = max(collateral_usd - debt_usd, 0.0) if metrics.eligible else 0.0
        
        logger.info("Liquidation simulation completed", extra={
            "extra_fields": {
                "position_id": position_id,
                "health_factor": metrics.health_factor,
                "eligible": metrics.eligible,
                "estimated_profit_usd": est_profit
            }
        })
        
        return LiquidationSimulateResponse(
            position_id=position_id,
            health_factor=metrics.health_factor,
            eligible=metrics.eligible,
            estimated_profit_usd=est_profit,
        )

    async def execute_liquidation(
        self, position_id: str, max_slippage_bps: int
    ) -> LiquidationExecuteResponse:
        """Execute liquidation with comprehensive error handling."""
        if not isinstance(max_slippage_bps, int) or max_slippage_bps < 0 or max_slippage_bps > 10000:
            raise ValueError("max_slippage_bps must be an integer between 0 and 10000")
        
        try:
            sim = await self.simulate_liquidation(position_id)
        except ValueError as e:
            raise ValueError(f"Simulation failed: {e}") from e
        
        if not sim.eligible:
            return LiquidationExecuteResponse(
                position_id=position_id, tx_hash="", realized_profit_usd=0.0
            )
        
        try:
            # Placeholder execution path - in real system would build and send tx via web3
            tx_hash = "0x" + (abs(hash(position_id)) % (10**16)).to_bytes(8, "big").hex()
            return LiquidationExecuteResponse(
                position_id=position_id,
                tx_hash=tx_hash,
                realized_profit_usd=sim.estimated_profit_usd or 0.0,
            )
        except Exception as e:
            raise ValueError(f"Execution failed: {e}") from e
