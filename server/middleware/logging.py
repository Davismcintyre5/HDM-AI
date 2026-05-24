# ====================================================================================================
# server/middleware/logging.py
# ====================================================================================================
"""
HDM AI - Request Logging Middleware
Logs all requests with unique IDs and response times
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time
import uuid


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        try:
            response: Response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"[{request_id}] {response.status_code} "
                f"completed in {process_time:.2f}ms"
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            return response
        except Exception as e:
            logger.error(f"[{request_id}] Error: {str(e)}")
            raise