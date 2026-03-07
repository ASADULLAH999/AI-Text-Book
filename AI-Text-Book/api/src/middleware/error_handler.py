"""
Error Handler Middleware
Provides standardized error responses across the API.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors with standardized format.

    Error response format:
    {
        "error": {
            "code": "error_code",
            "message": "Human-readable message",
            "details": "Additional details",
            "timestamp": "ISO timestamp",
            "request_id": "request-id",
            "path": "/api/v1/chat"
        }
    }
    """

    async def dispatch(self, request: Request, call_next):
        """Process the request and handle any errors."""
        try:
            response = await call_next(request)
            return response

        except Exception as e:
            return self._handle_exception(request, e)

    def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle exception and return standardized error response.

        Args:
            request: FastAPI request
            exc: Exception that occurred

        Returns:
            JSONResponse with error details
        """
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")

        # Determine error type and status code
        error_info = self._get_error_info(exc)

        # Log the error
        self._log_error(request, exc, error_info, request_id)

        # Build error response
        error_response = {
            "error": {
                "code": error_info["code"],
                "message": error_info["message"],
                "details": error_info.get("details"),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "path": request.url.path,
            }
        }

        # Add stack trace in development mode
        if self._is_development():
            error_response["error"]["traceback"] = traceback.format_exc()

        return JSONResponse(
            status_code=error_info["status_code"],
            content=error_response,
        )

    def _get_error_info(self, exc: Exception) -> Dict[str, Any]:
        """
        Extract error information from exception.

        Args:
            exc: Exception

        Returns:
            Dictionary with error code, message, status code
        """
        # Handle FastAPI HTTPException
        from fastapi import HTTPException

        if isinstance(exc, HTTPException):
            return {
                "code": self._get_error_code(exc.status_code),
                "message": exc.detail,
                "status_code": exc.status_code,
            }

        # Handle ValueError (validation errors)
        if isinstance(exc, ValueError):
            return {
                "code": "validation_error",
                "message": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
            }

        # Handle TypeError
        if isinstance(exc, TypeError):
            return {
                "code": "type_error",
                "message": "Invalid data type in request",
                "details": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
            }

        # Handle KeyError
        if isinstance(exc, KeyError):
            return {
                "code": "missing_field",
                "message": f"Required field missing: {str(exc)}",
                "status_code": status.HTTP_400_BAD_REQUEST,
            }

        # Handle timeout errors
        if isinstance(exc, TimeoutError):
            return {
                "code": "request_timeout",
                "message": "Request timed out",
                "status_code": status.HTTP_504_GATEWAY_TIMEOUT,
            }

        # Handle connection errors
        if "Connection" in exc.__class__.__name__:
            return {
                "code": "service_unavailable",
                "message": "Unable to connect to required service",
                "details": str(exc),
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            }

        # Default: Internal server error
        return {
            "code": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": str(exc) if self._is_development() else None,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    def _get_error_code(self, status_code: int) -> str:
        """
        Get error code string from HTTP status code.

        Args:
            status_code: HTTP status code

        Returns:
            Error code string
        """
        error_codes = {
            400: "bad_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            405: "method_not_allowed",
            408: "request_timeout",
            409: "conflict",
            413: "payload_too_large",
            415: "unsupported_media_type",
            422: "unprocessable_entity",
            429: "rate_limit_exceeded",
            500: "internal_server_error",
            502: "bad_gateway",
            503: "service_unavailable",
            504: "gateway_timeout",
        }

        return error_codes.get(status_code, "unknown_error")

    def _log_error(
        self,
        request: Request,
        exc: Exception,
        error_info: Dict[str, Any],
        request_id: str,
    ) -> None:
        """
        Log the error with appropriate level.

        Args:
            request: FastAPI request
            exc: Exception
            error_info: Error information dict
            request_id: Request ID
        """
        log_extra = {
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error_code": error_info["code"],
            "status_code": error_info["status_code"],
        }

        # Log level based on status code
        if error_info["status_code"] >= 500:
            logger.error(
                f"Server error: {exc}",
                extra=log_extra,
                exc_info=True,
            )
        elif error_info["status_code"] >= 400:
            logger.warning(
                f"Client error: {exc}",
                extra=log_extra,
            )
        else:
            logger.info(
                f"Request error: {exc}",
                extra=log_extra,
            )

    def _is_development(self) -> bool:
        """Check if running in development mode."""
        import os

        return os.getenv("ENVIRONMENT", "development").lower() in [
            "development",
            "dev",
            "local",
        ]


# Error response builders
def build_error_response(
    code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a standardized error response.

    Args:
        code: Error code
        message: Error message
        status_code: HTTP status code
        details: Optional additional details
        request_id: Optional request ID

    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
        },
        "status_code": status_code,
    }


def build_validation_error(
    field: str,
    message: str,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a validation error response.

    Args:
        field: Field that failed validation
        message: Validation error message
        request_id: Optional request ID

    Returns:
        Validation error response
    """
    return build_error_response(
        code="validation_error",
        message=f"Validation failed for field '{field}': {message}",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id,
    )
