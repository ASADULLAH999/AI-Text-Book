"""
Structured JSON Logging Middleware
Logs all requests and responses with structured metadata for observability.
"""

import json
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
)

logger = logging.getLogger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with structured JSON format."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log structured information."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Extract request metadata
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request
        log_data = {
            "event": "request_received",
            "request_id": request_id,
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": client_host,
            "user_agent": user_agent,
        }
        logger.info(json.dumps(log_data))

        # Process request
        try:
            response = await call_next(request)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Log response
            response_log_data = {
                "event": "request_completed",
                "request_id": request_id,
                "timestamp": time.time(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            }
            logger.info(json.dumps(response_log_data))

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log error
            latency_ms = int((time.time() - start_time) * 1000)
            error_log_data = {
                "event": "request_error",
                "request_id": request_id,
                "timestamp": time.time(),
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": type(e).__name__,
                "latency_ms": latency_ms,
            }
            logger.error(json.dumps(error_log_data))
            raise


def log_chat_query(
    request_id: str,
    query: str,
    mode: str,
    user_id: str = None,
    **kwargs,
):
    """Log structured data for chat queries."""
    log_data = {
        "event": "chat_query",
        "request_id": request_id,
        "timestamp": time.time(),
        "query": query,
        "mode": mode,
        "user_id": user_id,
        "query_length": len(query),
        **kwargs,
    }
    logger.info(json.dumps(log_data))


def log_retrieval(
    request_id: str,
    chunks_retrieved: int,
    chunks_used: int,
    avg_similarity: float,
    latency_ms: int,
):
    """Log retrieval metrics."""
    log_data = {
        "event": "retrieval_completed",
        "request_id": request_id,
        "timestamp": time.time(),
        "chunks_retrieved": chunks_retrieved,
        "chunks_used": chunks_used,
        "avg_similarity": avg_similarity,
        "latency_ms": latency_ms,
    }
    logger.info(json.dumps(log_data))


def log_generation(
    request_id: str,
    model: str,
    temperature: float,
    tokens_used: int,
    latency_ms: int,
):
    """Log generation metrics."""
    log_data = {
        "event": "generation_completed",
        "request_id": request_id,
        "timestamp": time.time(),
        "model": model,
        "temperature": temperature,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
    }
    logger.info(json.dumps(log_data))


def log_citation_validation(
    request_id: str,
    citations_count: int,
    confidence_avg: float,
    latency_ms: int,
):
    """Log citation validation metrics."""
    log_data = {
        "event": "citation_validation_completed",
        "request_id": request_id,
        "timestamp": time.time(),
        "citations_count": citations_count,
        "confidence_avg": confidence_avg,
        "latency_ms": latency_ms,
    }
    logger.info(json.dumps(log_data))


def log_error(
    request_id: str,
    error_code: str,
    error_message: str,
    **kwargs,
):
    """Log structured error information."""
    log_data = {
        "event": "error",
        "request_id": request_id,
        "timestamp": time.time(),
        "error_code": error_code,
        "error_message": error_message,
        **kwargs,
    }
    logger.error(json.dumps(log_data))
