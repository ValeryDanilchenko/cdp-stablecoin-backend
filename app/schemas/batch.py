from typing import Any

from pydantic import BaseModel, Field

from app.schemas.position import PositionCreate


class BatchPositionCreateRequest(BaseModel):
    """Request to create multiple positions in batch."""
    
    positions: list[PositionCreate] = Field(
        description="List of positions to create",
        min_length=1,
        max_length=100
    )


class PositionCreateResult(BaseModel):
    """Result of a single position creation."""
    
    id: int = Field(description="Database ID of created position")
    position_id: str = Field(description="Position identifier")
    owner_address: str = Field(description="Owner Ethereum address")
    collateral_symbol: str = Field(description="Collateral token symbol")
    collateral_amount: str = Field(description="Collateral amount")
    debt_symbol: str = Field(description="Debt token symbol")
    debt_amount: str = Field(description="Debt amount")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


class PositionCreateError(BaseModel):
    """Error from a single position creation."""
    
    index: int = Field(description="Index of the position in the request")
    position_id: str = Field(description="Position identifier that failed")
    error: str = Field(description="Error message")


class BatchPositionCreateResponse(BaseModel):
    """Response from batch position creation."""
    
    created_count: int = Field(description="Number of positions successfully created")
    error_count: int = Field(description="Number of positions that failed to create")
    positions: list[PositionCreateResult] = Field(description="Successfully created positions")
    errors: list[PositionCreateError] = Field(description="Creation errors")


class BatchSimulationRequest(BaseModel):
    """Request to simulate multiple liquidations."""
    
    position_ids: list[str] = Field(
        description="List of position IDs to simulate",
        min_length=1,
        max_length=50
    )


class SimulationResult(BaseModel):
    """Result of a single liquidation simulation."""
    
    position_id: str = Field(description="Position identifier")
    health_factor: float = Field(description="Current health factor")
    eligible: bool = Field(description="Whether position is eligible for liquidation")
    estimated_profit_usd: float = Field(description="Estimated profit in USD")


class SimulationError(BaseModel):
    """Error from a single simulation."""
    
    index: int = Field(description="Index of the position in the request")
    position_id: str = Field(description="Position identifier that failed")
    error: str = Field(description="Error message")


class BatchSimulationResponse(BaseModel):
    """Response from batch liquidation simulation."""
    
    simulated_count: int = Field(description="Number of positions successfully simulated")
    error_count: int = Field(description="Number of positions that failed to simulate")
    results: list[SimulationResult] = Field(description="Simulation results")
    errors: list[SimulationError] = Field(description="Simulation errors")


class LiquidationRequest(BaseModel):
    """Single liquidation request."""
    
    position_id: str = Field(description="Position identifier to liquidate")
    max_slippage_bps: int = Field(
        description="Maximum acceptable slippage in basis points",
        ge=0,
        le=10000
    )


class BatchLiquidationRequest(BaseModel):
    """Request to execute multiple liquidations."""
    
    liquidations: list[LiquidationRequest] = Field(
        description="List of liquidation requests",
        min_length=1,
        max_length=20
    )


class LiquidationResult(BaseModel):
    """Result of a single liquidation execution."""
    
    position_id: str = Field(description="Position identifier")
    tx_hash: str = Field(description="Transaction hash")
    realized_profit_usd: float = Field(description="Realized profit in USD")


class LiquidationError(BaseModel):
    """Error from a single liquidation."""
    
    index: int = Field(description="Index of the liquidation in the request")
    position_id: str = Field(description="Position identifier that failed")
    error: str = Field(description="Error message")


class BatchLiquidationResponse(BaseModel):
    """Response from batch liquidation execution."""
    
    executed_count: int = Field(description="Number of liquidations successfully executed")
    error_count: int = Field(description="Number of liquidations that failed")
    results: list[LiquidationResult] = Field(description="Execution results")
    errors: list[LiquidationError] = Field(description="Execution errors")
