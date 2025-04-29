from typing import Any, Dict

from fastapi import Request, Response

from app.core.logging_service import BaseLoggingService


class MockLoggingService(BaseLoggingService):
    """Mock logging service for testing"""

    async def log_request(self, request: Request) -> None:
        """Mock implementation of log_request"""
        pass

    async def log_response(self, response: Response, request: Request) -> None:
        """Mock implementation of log_response"""
        pass

    async def log_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Mock implementation of log_business_event"""
        pass

    async def log_api_exception(self, exception: Exception) -> None:
        """Mock implementation of log_api_exception"""
        pass

    async def log_business_exception(self, exception: Exception) -> None:
        """Mock implementation of log_business_exception"""
        pass
