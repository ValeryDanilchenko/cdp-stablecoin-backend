from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes.batch import router as batch_router
from app.api.routes.health import router as health_router
from app.api.routes.liquidation import router as liquidation_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.positions import router as positions_router
from app.core.config import settings
from app.core.rate_limiting import rate_limit_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="CDP Demo API",
        description="""
        ## Collateralized Debt Position Management API
        
        This API provides comprehensive management of Collateralized Debt Positions (CDPs) with:
        
        * **Position Management**: Create, list, and manage CDP positions
        * **Liquidation System**: Simulate and execute liquidations
        * **Risk Assessment**: Real-time health factor calculations
        * **Price Oracle**: Token price feeds with volatility simulation
        
        ### Key Features
        
        - ?? **Secure**: Input validation and error handling
        - ?? **Observable**: Structured logging and metrics
        - ?? **Scalable**: Async/await architecture
        - ?? **Deployable**: Docker-ready with production configs
        
        ### Authentication
        
        Currently no authentication required. In production, implement JWT or API key authentication.
        
        ### Rate Limiting
        
        API calls are rate limited to prevent abuse. Contact support for higher limits.
        """,
        version="1.0.0",
        contact={
            "name": "CDP Demo Team",
            "email": "support@cdpdemo.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.cdpdemo.com",
                "description": "Production server"
            }
        ],
        openapi_tags=[
            {
                "name": "health",
                "description": "Health check endpoints for monitoring"
            },
            {
                "name": "positions",
                "description": "CDP position management operations"
            },
            {
                "name": "liquidation",
                "description": "Liquidation simulation and execution"
            },
            {
                "name": "metrics",
                "description": "System metrics and monitoring data"
            },
            {
                "name": "batch",
                "description": "Batch operations for multiple positions"
            }
        ]
    )

    # Add rate limiting middleware
    app.middleware("http")(rate_limit_middleware)

    # Routers
    app.include_router(health_router)
    app.include_router(positions_router)
    app.include_router(liquidation_router, prefix="/liquidation", tags=["liquidation"])
    app.include_router(metrics_router)
    app.include_router(batch_router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level="info",
        workers=1,
    )
