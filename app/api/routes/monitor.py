from fastapi import APIRouter, HTTPException

from app.services.monitor import ContractsMonitor
from app.db.session import get_sessionmaker

router = APIRouter(prefix="/monitor", tags=["monitor"]) 

_monitor = ContractsMonitor(sessionmaker=get_sessionmaker())


@router.post("/start")
async def start_monitor() -> dict[str, str]:
    if _monitor.is_running():
        raise HTTPException(status_code=409, detail="monitor already running")
    await _monitor.start()
    return {"status": "started"}


@router.post("/stop")
async def stop_monitor() -> dict[str, str]:
    if not _monitor.is_running():
        return {"status": "stopped"}
    await _monitor.stop()
    return {"status": "stopped"}


@router.get("/status")
async def monitor_status() -> dict[str, object]:
    s = _monitor.status()
    return {
        "running": s.running,
        "last_tick_at": s.last_tick_at.isoformat() if s.last_tick_at else None,
        "processed_blocks": s.processed_blocks,
    }
