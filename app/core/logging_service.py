import json
import logging
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Annotated, Any, Dict

from fastapi import Depends, Request, Response
from loguru import logger

from app.core.config import settings


class BaseLoggingService(ABC):
    """Abstract base class for logging services"""

    @abstractmethod
    async def log_request(self, request: Request) -> None:
        """Log incoming HTTP request"""
        pass

    @abstractmethod
    async def log_response(self, response: Response, request: Request) -> None:
        """Log outgoing HTTP response"""
        pass

    @abstractmethod
    async def log_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log business-specific events"""
        pass

    @abstractmethod
    async def log_api_exception(self, exception: Exception) -> None:
        """Log API exceptions"""
        pass

    @abstractmethod
    async def log_business_exception(self, exception: Exception) -> None:
        """Log business-specific exceptions"""
        pass


class ConsoleLoggingService(BaseLoggingService):
    """Development logging service that logs to console using Loguru"""

    def __init__(self):
        # Ensure only one handler to avoid duplicates
        logger.remove()

        # Add a new console (stdout) handler
        logger.add(
            sink=sys.stdout,
            level="DEBUG",
            format=(
                "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | "
                "<yellow><level>{level}</level></yellow> | "
                "<green>{message}</green>"
            ),
            colorize=True,
        )

        self.logger = logger

    async def log_request(self, request: Request) -> None:
        self.logger.info(
            json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "request",
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "client": request.client.host if request.client else None,
                }
            )
        )

    async def log_response(self, response: Response, request: Request) -> None:
        self.logger.info(
            json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "response",
                    "status_code": response.status_code,
                    "method": request.method,
                    "url": str(request.url),
                }
            )
        )

    async def log_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        self.logger.info(
            json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "business_event",
                    "event_type": event_type,
                    "data": data,
                }
            )
        )

    async def log_api_exception(self, exception: Exception) -> None:
        self.logger.error(
            json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "api_exception",
                    "exception": str(exception),
                }
            )
        )

    async def log_business_exception(self, exception: Exception) -> None:
        self.logger.error(
            json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "business_exception",
                    "exception": str(exception),
                }
            )
        )


class ExternalLoggingService(BaseLoggingService):
    """Production logging service that sends logs to external service"""

    def __init__(self):
        # Initialize connection to external logging service
        # This is a placeholder - implement actual external service connection
        self.logger = logging.getLogger("external")
        self.logger.setLevel(logging.INFO)

    async def log_request(self, request: Request) -> None:
        """Log incoming HTTP request to external service"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "request",
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
        }
        # TODO: Implement actual external service logging
        self.logger.info(json.dumps(log_data))

    async def log_response(self, response: Response, request: Request) -> None:
        """Log outgoing HTTP response to external service"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "response",
            "status_code": response.status_code,
            "method": request.method,
            "url": str(request.url),
        }
        # TODO: Implement actual external service logging
        self.logger.info(json.dumps(log_data))

    async def log_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log business-specific events to external service"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "business_event",
            "event_type": event_type,
            "data": data,
        }
        # TODO: Implement actual external service logging
        self.logger.info(json.dumps(log_data))

    async def log_api_exception(self, exception: Exception) -> None:
        """Log API exceptions to external service"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "api_exception",
            "exception": str(exception),
        }
        # TODO: Implement actual external service logging
        self.logger.error(json.dumps(log_data))

    async def log_business_exception(self, exception: Exception) -> None:
        """Log business-specific exceptions to external service"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "business_exception",
            "exception": str(exception),
        }
        # TODO: Implement actual external service logging
        self.logger.error(json.dumps(log_data))


# Create a singleton for the logging service
def get_logging_service() -> BaseLoggingService:
    """Factory function to get the appropriate logging service based on environment"""
    if settings.ENV == "production":
        return ExternalLoggingService()
    return ConsoleLoggingService()


# Type annotation for the logging service dependency
LoggingServiceDep = Annotated[BaseLoggingService, Depends(get_logging_service)]
