"""Error codes and global exception handlers."""
import logging
from enum import StrEnum
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import current_request_id
from app.schemas.common import ApiResponse

logger = logging.getLogger("app.errors")


class ErrorCode(StrEnum):
    OK = "OK"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    HTTP_ERROR = "HTTP_ERROR"
    NOT_READY = "NOT_READY"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.METHOD_NOT_ALLOWED: 405,
    ErrorCode.NOT_IMPLEMENTED: 501,
    ErrorCode.HTTP_ERROR: 400,
    ErrorCode.NOT_READY: 503,
    ErrorCode.INTERNAL_ERROR: 500,
}

DEFAULT_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.VALIDATION_ERROR: "请求参数校验失败",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.METHOD_NOT_ALLOWED: "请求方法不被允许",
    ErrorCode.NOT_IMPLEMENTED: "该能力尚未实现",
    ErrorCode.HTTP_ERROR: "HTTP 请求错误",
    ErrorCode.NOT_READY: "依赖未就绪",
    ErrorCode.INTERNAL_ERROR: "服务内部错误",
}


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str | None = None,
        details: Any = None,
        status: int | None = None,
    ) -> None:
        self.code = code
        self.message = message or DEFAULT_MESSAGES[code]
        self.details = details
        self.status = status or ERROR_HTTP_STATUS[code]
        super().__init__(self.message)


def error_response(
    code: ErrorCode,
    message: str | None = None,
    details: Any = None,
    status: int | None = None,
) -> JSONResponse:
    payload = ApiResponse(
        code=code.value,
        message=message or DEFAULT_MESSAGES[code],
        data=details,
        request_id=current_request_id(),
    )
    return JSONResponse(
        status_code=status or ERROR_HTTP_STATUS[code],
        content=payload.model_dump(mode="json"),
        headers={"X-Error-Code": code.value},
    )


def validation_details(exc: RequestValidationError) -> list[dict]:
    # Keep location/message/type only: never echo submitted values into logs.
    return [
        {
            "loc": [str(part) for part in err.get("loc", [])],
            "msg": err.get("msg"),
            "type": err.get("type"),
        }
        for err in exc.errors()
    ]


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.code, exc.message, exc.details, exc.status)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(
            ErrorCode.VALIDATION_ERROR,
            details={"errors": validation_details(exc)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            code = ErrorCode.NOT_FOUND
        elif exc.status_code == 405:
            code = ErrorCode.METHOD_NOT_ALLOWED
        elif exc.status_code >= 500:
            code = ErrorCode.INTERNAL_ERROR
        else:
            code = ErrorCode.HTTP_ERROR
        return error_response(code, str(exc.detail), status=exc.status_code)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        _ = exc  # full traceback goes to the structured log, never to the client
        logger.exception(
            "unhandled exception",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error_code": ErrorCode.INTERNAL_ERROR.value,
            },
        )
        return error_response(ErrorCode.INTERNAL_ERROR)
