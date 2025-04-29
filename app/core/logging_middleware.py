from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from app.core.logging_service import BaseLoggingService


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """

    def __init__(self, app: ASGIApp, logging_service: BaseLoggingService):
        super().__init__(app)
        self.logging_service = logging_service

    async def dispatch(self, request: Request, call_next):
        # Log the incoming request
        await self.logging_service.log_request(request)

        # Process the request
        response = await call_next(request)

        # Log the outgoing response
        await self.logging_service.log_response(response, request)

        return response
