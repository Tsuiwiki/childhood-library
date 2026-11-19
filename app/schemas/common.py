"""Unified API envelope. Every success and error response uses this shape."""
from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: str = Field(..., description="统一业务错误码，成功为 OK")
    message: str
    data: Any | None = None
    request_id: str
