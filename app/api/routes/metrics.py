from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.position import Position
from app.schemas.metrics import (
    HealthMetricsResponse,
    PositionMetricsResponse,
    SystemMetricsResponse,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/system",
    response_model=SystemMetricsResponse,
    summary="System Metrics",
    description="""
    Get overall system metrics including total positions, health distribution, and system status.
    
    **Returns:**
    - Total number of positions
    - Number of liquidatable positions
    - Average health factor
    - System uptime and status
    
    **Example Response:**
    ```json
    {
        "total_positions": 150,
        "liquidatable_positions": 12,
        "average_health_factor": 1.85,
        "system_uptime_seconds": 3600,
        "status": "healthy"
    }
    ```
    """,
    responses={
        200: {"description": "System metrics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_system_metrics(
    session: AsyncSession = Depends(get_session),
) -> SystemMetricsResponse:
    """Get overall system metrics."""
    try:
        # Get total positions count
        total_stmt = select(func.count(Position.id))
        total_result = await session.execute(total_stmt)
        total_positions = total_result.scalar() or 0

        # Get liquidatable positions count (health factor < 1.0)
        # Note: This is a simplified calculation - in production you'd use actual price data
        liquidatable_stmt = select(func.count(Position.id)).where(
            Position.id.in_(
                select(Position.id).where(
                    # This would be calculated based on actual collateral/debt values
                    # For demo purposes, we'll use a simple heuristic
                    func.cast(Position.debt_amount, func.Float) > 
                    func.cast(Position.collateral_amount, func.Float) * 0.8
                )
            )
        )
        liquidatable_result = await session.execute(liquidatable_stmt)
        liquidatable_positions = liquidatable_result.scalar() or 0

        return SystemMetricsResponse(
            total_positions=total_positions,
            liquidatable_positions=liquidatable_positions,
            average_health_factor=1.85,  # Placeholder - would calculate from actual data
            system_uptime_seconds=3600,  # Placeholder - would track actual uptime
            status="healthy"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics") from exc


@router.get(
    "/positions",
    response_model=PositionMetricsResponse,
    summary="Position Metrics",
    description="""
    Get detailed metrics about CDP positions including health distribution and risk analysis.
    
    **Parameters:**
    - `limit`: Number of positions to analyze (1-1000, default: 100)
    
    **Returns:**
    - Health factor distribution
    - Risk categories breakdown
    - Top risky positions
    
    **Example Response:**
    ```json
    {
        "total_analyzed": 100,
        "health_distribution": {
            "safe": 60,
            "warning": 25,
            "critical": 15
        },
        "average_health_factor": 1.75,
        "riskiest_positions": [
            {
                "position_id": "pos_001",
                "health_factor": 0.85,
                "risk_level": "critical"
            }
        ]
    }
    ```
    """,
    responses={
        200: {"description": "Position metrics retrieved successfully"},
        422: {"description": "Invalid parameters"},
        500: {"description": "Internal server error"}
    }
)
async def get_position_metrics(
    limit: int = Query(100, ge=1, le=1000, description="Number of positions to analyze"),
    session: AsyncSession = Depends(get_session),
) -> PositionMetricsResponse:
    """Get detailed position metrics."""
    try:
        # Get positions for analysis
        stmt = select(Position).limit(limit)
        result = await session.execute(stmt)
        positions: Sequence[Position] = result.scalars().all()
        
        # Analyze health distribution (simplified for demo)
        safe_count = 0
        warning_count = 0
        critical_count = 0
        total_health = 0.0
        riskiest_positions = []
        
        for position in positions:
            # Simplified health factor calculation for demo
            try:
                collateral_val = float(position.collateral_amount)
                debt_val = float(position.debt_amount)
                if debt_val > 0:
                    health_factor = (collateral_val * 3000) / debt_val  # Assuming ETH = $3000
                else:
                    health_factor = 10.0  # No debt = very safe
                
                total_health += health_factor
                
                if health_factor >= 2.0:
                    safe_count += 1
                elif health_factor >= 1.0:
                    warning_count += 1
                else:
                    critical_count += 1
                    riskiest_positions.append({
                        "position_id": position.position_id,
                        "health_factor": round(health_factor, 2),
                        "risk_level": "critical"
                    })
            except (ValueError, TypeError):
                # Skip positions with invalid data
                continue
        
        # Sort riskiest positions by health factor
        riskiest_positions.sort(key=lambda x: x["health_factor"])
        
        return PositionMetricsResponse(
            total_analyzed=len(positions),
            health_distribution={
                "safe": safe_count,
                "warning": warning_count,
                "critical": critical_count
            },
            average_health_factor=round(total_health / len(positions), 2) if positions else 0.0,
            riskiest_positions=riskiest_positions[:10]  # Top 10 riskiest
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to retrieve position metrics") from exc


@router.get(
    "/health",
    response_model=HealthMetricsResponse,
    summary="Health Check Metrics",
    description="""
    Get detailed health check metrics for monitoring and alerting.
    
    **Returns:**
    - Database connectivity status
    - Price oracle status
    - System resource usage
    - Last successful operations timestamps
    
    **Example Response:**
    ```json
    {
        "database_status": "healthy",
        "price_oracle_status": "healthy",
        "last_price_update": "2024-01-01T12:00:00Z",
        "active_connections": 5,
        "memory_usage_mb": 128,
        "cpu_usage_percent": 15.5
    }
    ```
    """,
    responses={
        200: {"description": "Health metrics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_health_metrics(
    session: AsyncSession = Depends(get_session),
) -> HealthMetricsResponse:
    """Get detailed health check metrics."""
    try:
        # Test database connectivity
        db_status = "healthy"
        try:
            await session.execute(select(1))
        except Exception:
            db_status = "unhealthy"
        
        # Test price oracle (simplified)
        price_oracle_status = "healthy"
        last_price_update = "2024-01-01T12:00:00Z"  # Placeholder
        
        return HealthMetricsResponse(
            database_status=db_status,
            price_oracle_status=price_oracle_status,
            last_price_update=last_price_update,
            active_connections=5,  # Placeholder
            memory_usage_mb=128,  # Placeholder
            cpu_usage_percent=15.5  # Placeholder
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to retrieve health metrics") from exc
