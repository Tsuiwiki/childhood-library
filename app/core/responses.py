"""Success envelope helper."""
from typing import Any

from app.core.context import current_request_id
from app.core.errors import ErrorCode
from app.schemas.common import ApiResponse


def ok(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(
        code=ErrorCode.OK.value,
        message=message,
        data=data,
        request_id=current_request_id(),
    )
