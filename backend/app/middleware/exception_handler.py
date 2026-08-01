from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.response import error_response
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for FastAPI."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return error_response(message=str(exc.detail), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation Exception: {exc.errors()}")
        return error_response(
            message="Request validation failed",
            status_code=422,
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return error_response(
            message="An unexpected server error occurred.",
            status_code=500,
        )
