from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.services.indexer import Web3Indexer

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MonitorStatus:
    running: bool
    last_tick_at: Optional[datetime]
    processed_blocks: int


class ContractsMonitor:
    def __init__(self, poll_interval_sec: float | None = None, sessionmaker: async_sessionmaker[AsyncSession] | None = None) -> None:
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._poll_interval = poll_interval_sec or settings.monitor_poll_interval_sec
        self._processed_blocks = 0
        self._last_tick_at: datetime | None = None
        self._sessionmaker = sessionmaker
        self._current_block = 0

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def status(self) -> MonitorStatus:
        return MonitorStatus(
            running=self.is_running(),
            last_tick_at=self._last_tick_at,
            processed_blocks=self._processed_blocks,
        )

    async def start(self) -> None:
        if self.is_running():
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run_loop(), name="contracts-monitor")
        logger.info("contracts monitor started")

    async def stop(self) -> None:
        if not self.is_running():
            return
        self._stop_event.set()
        assert self._task is not None
        await self._task
        logger.info("contracts monitor stopped")

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self._tick()
            except Exception as exc:  # noqa: BLE001
                logger.exception("monitor loop error: %s", exc)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._poll_interval)
            except asyncio.TimeoutError:
                pass

    async def _tick(self) -> None:
        # Demo: index next block using indexer if sessionmaker provided
        if self._sessionmaker is not None:
            async with self._sessionmaker() as session:
                await Web3Indexer(session).index_block_range(self._current_block, self._current_block)
        self._current_block += 1
        self._processed_blocks += 1
        self._last_tick_at = datetime.utcnow()
