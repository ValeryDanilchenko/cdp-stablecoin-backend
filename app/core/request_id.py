import logging
import uuid
from typing import Callable

from fastapi import Request

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def request_id_middleware():
    async def _middleware(request: Request, call_next: Callable):
        req_id = request.headers.get(_REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers[_REQUEST_ID_HEADER] = req_id
        return response

    return _middleware
