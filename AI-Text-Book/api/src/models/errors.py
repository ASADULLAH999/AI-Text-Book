"""Error response models for API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for API responses."""

    RETRIEVAL_FAILED = "RETRIEVAL_FAILED"
    GENERATION_FAILED = "GENERATION_FAILED"
    INVALID_MODE = "INVALID_MODE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: str = Field(..., description="Additional context about the error")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Error timestamp"
    )
    request_id: str = Field(..., description="Request ID for tracing")

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "RETRIEVAL_FAILED",
                "message": "No relevant textbook content found",
                "details": "Query: 'quantum mechanics basics'",
                "timestamp": "2026-02-05T10:30:00Z",
                "request_id": "req_abc123",
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: ErrorDetail = Field(..., description="Error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": {
                    "code": "RETRIEVAL_FAILED",
                    "message": "No relevant textbook content found",
                    "details": "Query: 'quantum mechanics basics'",
                    "timestamp": "2026-02-05T10:30:00Z",
                    "request_id": "req_abc123",
                }
            }
        }
    }
