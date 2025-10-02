from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.metrics import metrics_endpoint
from app.core.request_id import request_id_middleware
from app.api.routes.health import router as health_router
from app.api.routes.liquidation import router as liquidation_router
from app.api.routes.positions import router as positions_router
from app.api.routes.monitor import router as monitor_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.events import router as events_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="CDP Skill Demo Backend", version="0.1.0")

    # Middlewares
    app.middleware("http")(request_id_middleware())

    # Metrics endpoint
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

    # Routers
    app.include_router(health_router)
    app.include_router(positions_router)
    app.include_router(monitor_router)
    app.include_router(analytics_router)
    app.include_router(events_router)
    app.include_router(liquidation_router, prefix="/liquidation", tags=["liquidation"])

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
