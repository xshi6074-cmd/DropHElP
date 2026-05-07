from typing import Any, Optional
from fastapi.responses import JSONResponse
import uuid


def api_response(
    data: Any = None,
    code: int = 0,
    message: str = "success",
    request_id: Optional[str] = None
) -> dict:
    """统一API响应格式"""
    return {
        "code": code,
        "data": data,
        "message": message,
        "requestId": request_id or str(uuid.uuid4())[:8]
    }


def api_error(
    message: str,
    code: int = 400,
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """错误响应"""
    return JSONResponse(
        status_code=status_code,
        content=api_response(data=data, code=code, message=message)
    )


class ErrorCode:
    """错误码枚举"""
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    AUTH_FAILED = 2000
    TOKEN_EXPIRED = 2001
    TOKEN_INVALID = 2002
    CODE_EXPIRED = 2003
    CODE_INVALID = 2004
    TOO_FREQUENT = 2005
    TASK_NOT_FOUND = 3000
    TASK_ALREADY_ACCEPTED = 3001
    TASK_EXPIRED = 3002
    ALREADY_HAS_TASK = 3003
    USER_NOT_FOUND = 4000
