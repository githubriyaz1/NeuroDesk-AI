from typing import Any
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    """Standardized JSON success response wrapper."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error_response(message: str = "An error occurred", status_code: int = 400, details: Any = None) -> JSONResponse:
    """Standardized JSON error response wrapper."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "details": details,
        },
    )
