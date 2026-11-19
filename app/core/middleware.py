"""Request context: request-id propagation + structured access log."""
import logging
import time
import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import request_id_var
from app.core.errors import ErrorCode

access_logger = logging.getLogger("app.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        request.state.request_id = request_id
        started = time.perf_counter()

        common = {
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
        }
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            access_logger.info(
                "request completed",
                extra={
                    **common,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "error_code": response.headers.get("X-Error-Code"),
                },
            )
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            access_logger.exception(
                "request failed",
                extra={
                    **common,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "error_code": ErrorCode.INTERNAL_ERROR.value,
                },
            )
            raise
        finally:
            request_id_var.reset(token)
