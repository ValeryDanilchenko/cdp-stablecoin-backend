from typing import Any

from pydantic import BaseModel, Field


class SystemMetricsResponse(BaseModel):
    """System-wide metrics response."""
    
    total_positions: int = Field(description="Total number of CDP positions")
    liquidatable_positions: int = Field(description="Number of positions eligible for liquidation")
    average_health_factor: float = Field(description="Average health factor across all positions")
    system_uptime_seconds: int = Field(description="System uptime in seconds")
    status: str = Field(description="Overall system status (healthy/warning/critical)")


class PositionRiskInfo(BaseModel):
    """Information about a risky position."""
    
    position_id: str = Field(description="Position identifier")
    health_factor: float = Field(description="Current health factor")
    risk_level: str = Field(description="Risk level (safe/warning/critical)")


class HealthDistribution(BaseModel):
    """Health factor distribution breakdown."""
    
    safe: int = Field(description="Number of safe positions (health_factor >= 2.0)")
    warning: int = Field(description="Number of warning positions (1.0 <= health_factor < 2.0)")
    critical: int = Field(description="Number of critical positions (health_factor < 1.0)")


class PositionMetricsResponse(BaseModel):
    """Detailed position metrics response."""
    
    total_analyzed: int = Field(description="Total number of positions analyzed")
    health_distribution: HealthDistribution = Field(description="Health factor distribution")
    average_health_factor: float = Field(description="Average health factor")
    riskiest_positions: list[PositionRiskInfo] = Field(
        description="List of riskiest positions",
        max_length=10
    )


class HealthMetricsResponse(BaseModel):
    """Detailed health check metrics response."""
    
    database_status: str = Field(description="Database connectivity status")
    price_oracle_status: str = Field(description="Price oracle service status")
    last_price_update: str = Field(description="Last successful price update timestamp")
    active_connections: int = Field(description="Number of active database connections")
    memory_usage_mb: float = Field(description="Memory usage in MB")
    cpu_usage_percent: float = Field(description="CPU usage percentage")
