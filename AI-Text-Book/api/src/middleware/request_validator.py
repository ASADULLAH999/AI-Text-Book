"""
Request Validation Middleware
Validates incoming requests before they reach the handlers.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# T107 — Input sanitization helpers
# ---------------------------------------------------------------------------

# Compiled patterns for performance
_XSS_PATTERNS = [
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on\w+\s*=\s*[\"']", re.IGNORECASE),
    re.compile(r"<\s*(iframe|object|embed|form|svg|math)", re.IGNORECASE),
    re.compile(r"expression\s*\(", re.IGNORECASE),
    re.compile(r"data\s*:\s*text/html", re.IGNORECASE),
]

_SQL_PATTERNS = [
    re.compile(r"(--|;|/\*|\*/)", re.IGNORECASE),
    re.compile(
        r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|EXECUTE|"
        r"CAST|CONVERT|DECLARE|CURSOR|FETCH|KILL|XP_)\b",
        re.IGNORECASE,
    ),
]

# Null byte and control characters (except tab/newline/CR)
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(text: str) -> str:
    """
    T107 — Strip null bytes and control characters from *text*.
    Does NOT block legitimate messages; strips only binary garbage.
    XSS/SQLi patterns are detected separately and flagged, not stripped,
    so the original error message is preserved for the end user.

    Returns the cleaned string.
    """
    return _CONTROL_CHAR_RE.sub("", text)


def detect_xss(text: str) -> bool:
    """Return True if *text* contains an XSS pattern."""
    return any(p.search(text) for p in _XSS_PATTERNS)


def detect_sqli(text: str) -> bool:
    """Return True if *text* looks like a SQL injection attempt."""
    return any(p.search(text) for p in _SQL_PATTERNS)


def validate_and_sanitize_message(message: str, max_length: int = 500) -> str:
    """
    T107 — Full sanitization pipeline for user chat messages.

    Steps:
      1. Strip control characters.
      2. Reject XSS patterns (HTTP 400).
      3. Reject SQL injection patterns (HTTP 400).
      4. Enforce max_length.

    Returns the sanitized message on success.
    Raises HTTPException on violation.
    """
    from fastapi import HTTPException, status  # local to avoid circular import

    cleaned = sanitize_text(message)

    if detect_xss(cleaned):
        logger.warning("T107: XSS pattern detected in message")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message contains disallowed content.",
        )

    if detect_sqli(cleaned):
        logger.warning("T107: SQL injection pattern detected in message")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message contains disallowed content.",
        )

    if len(cleaned) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message too long. Maximum {max_length} characters allowed.",
        )

    return cleaned


class RequestValidatorMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating requests.

    Validates:
    - Content-Type headers
    - Request size limits
    - Query parameter formats
    - Header requirements
    """

    def __init__(
        self,
        app,
        max_content_length: int = 10 * 1024 * 1024,  # 10MB
        allowed_content_types: Optional[List[str]] = None,
    ):
        """
        Initialize request validator.

        Args:
            app: FastAPI application
            max_content_length: Maximum request body size in bytes
            allowed_content_types: Allowed Content-Type headers
        """
        super().__init__(app)
        self.max_content_length = max_content_length
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process the request through validation."""
        try:
            # Skip validation for OPTIONS requests (CORS preflight)
            if request.method == "OPTIONS":
                return await call_next(request)

            # Skip validation for GET requests and health checks
            if request.method == "GET" or request.url.path in ["/", "/health", "/api/v1/health"]:
                return await call_next(request)

            # Validate Content-Type for POST/PUT/PATCH
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "").split(";")[0].strip()

                if content_type and content_type not in self.allowed_content_types:
                    logger.warning(
                        f"Invalid Content-Type: {content_type}",
                        extra={"path": request.url.path, "method": request.method},
                    )
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f"Content-Type '{content_type}' not supported. "
                        f"Allowed: {', '.join(self.allowed_content_types)}",
                    )

            # Validate Content-Length
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    content_length_int = int(content_length)
                    if content_length_int > self.max_content_length:
                        logger.warning(
                            f"Request too large: {content_length_int} bytes",
                            extra={"path": request.url.path},
                        )
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Request body too large. Maximum size: {self.max_content_length} bytes",
                        )
                except ValueError:
                    logger.warning(f"Invalid Content-Length header: {content_length}")

            # Validate query parameters (basic XSS prevention)
            for key, value in request.query_params.items():
                if not self._is_safe_query_param(value):
                    logger.warning(
                        f"Suspicious query parameter detected: {key}={value[:50]}",
                        extra={"path": request.url.path},
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid query parameter: {key}",
                    )

            # Continue to next middleware/handler
            response = await call_next(request)
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Request validation error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request validation failed",
            )

    def _is_safe_query_param(self, value: str) -> bool:
        """
        Check if query parameter value is safe.

        Args:
            value: Query parameter value

        Returns:
            True if safe, False otherwise
        """
        # Check for common XSS patterns
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",  # Event handlers like onclick=
            r"<iframe",
            r"<object",
            r"<embed",
        ]

        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower):
                return False

        return True


# Validation utilities
def validate_message_length(message: str, max_length: int = 500) -> None:
    """
    Validate message length.

    Args:
        message: Message text
        max_length: Maximum allowed length

    Raises:
        HTTPException: If message exceeds max length
    """
    if len(message) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message too long. Maximum {max_length} characters allowed.",
        )


def validate_mode(mode: str, allowed_modes: List[str]) -> None:
    """
    Validate chat mode.

    Args:
        mode: Chat mode
        allowed_modes: List of allowed modes

    Raises:
        HTTPException: If mode is invalid
    """
    if mode not in allowed_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode '{mode}'. Allowed modes: {', '.join(allowed_modes)}",
        )


def validate_filters(filters: dict) -> None:
    """
    Validate metadata filters.

    Args:
        filters: Filter dictionary

    Raises:
        HTTPException: If filters are invalid
    """
    if not isinstance(filters, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filters must be a dictionary",
        )

    # Validate filter keys (metadata fields)
    allowed_keys = ["chapter", "section", "heading", "page_number"]
    for key in filters.keys():
        if key not in allowed_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filter key '{key}'. Allowed: {', '.join(allowed_keys)}",
            )

    # Validate values are not empty
    for key, value in filters.items():
        if not value or (isinstance(value, str) and not value.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filter value for '{key}' cannot be empty",
            )
