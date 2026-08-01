import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestTimingLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware logging incoming requests, processing duration, and response status."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time_ms:.2f}ms"
        )
        return response
