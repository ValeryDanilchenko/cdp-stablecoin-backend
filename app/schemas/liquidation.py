from pydantic import BaseModel, Field


class LiquidationSimulateResponse(BaseModel):
    position_id: str
    health_factor: float = Field(ge=0)
    eligible: bool
    estimated_profit_usd: float | None = None


class LiquidationExecuteRequest(BaseModel):
    position_id: str
    max_slippage_bps: int = Field(ge=0, le=10_000)


class LiquidationExecuteResponse(BaseModel):
    position_id: str
    tx_hash: str
    realized_profit_usd: float
