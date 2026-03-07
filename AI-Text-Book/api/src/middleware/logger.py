"""
Structured JSON Logging Middleware
Logs all requests and responses with structured metadata for observability.
"""

import json
import time
import uuid
from typing import Callable, Optional
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
    user_id: Optional[str] = None,
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


# ---------------------------------------------------------------------------
# T062 [US2] — Selection metadata logging
# ---------------------------------------------------------------------------

def log_selection_query(
    request_id: str,
    query: str,
    selection_token_count: int,
    selection_char_count: int,
    is_valid: bool,
    refusal_reason: Optional[str] = None,
    source_hint: Optional[dict] = None,
):
    """
    Log a Selected-Text mode query with selection metadata.

    Args:
        request_id: Unique request identifier
        query: The user's question
        selection_token_count: Estimated token count of the selection
        selection_char_count: Character count of the selection
        is_valid: Whether the selection passed boundary validation
        refusal_reason: Reason for refusal when is_valid is False
        source_hint: Optional chapter/section context hints
    """
    log_data = {
        "event": "selected_text_query",
        "request_id": request_id,
        "timestamp": time.time(),
        "query": query,
        "mode": "selected_text",
        "query_length": len(query),
        "selection_token_count": selection_token_count,
        "selection_char_count": selection_char_count,
        "selection_is_valid": is_valid,
        "vector_searches_performed": 0,  # Invariant for this mode
        "source_hint": source_hint or {},
    }

    if refusal_reason:
        log_data["refusal_reason"] = refusal_reason

    logger.info(json.dumps(log_data))


# ---------------------------------------------------------------------------
# T076 [US3] — Mode switch logging
# ---------------------------------------------------------------------------

def log_mode_switch(
    request_id: str,
    from_mode: str,
    to_mode: str,
    user_id: Optional[str] = None,
):
    """
    Log when the user switches between answering modes.

    Args:
        request_id: Unique request identifier
        from_mode: The mode being left
        to_mode: The mode being entered
        user_id: Optional user identifier for analytics
    """
    log_data = {
        "event": "mode_switch",
        "request_id": request_id,
        "timestamp": time.time(),
        "from_mode": from_mode,
        "to_mode": to_mode,
    }
    if user_id:
        log_data["user_id"] = user_id
    logger.info(json.dumps(log_data))


# ---------------------------------------------------------------------------
# T118 — Request ID propagation helper
# ---------------------------------------------------------------------------

def get_request_id(request) -> str:
    """
    T118 — Extract or generate a request ID for end-to-end tracing.
    Prefers the X-Request-ID header (set by upstream proxy/client).
    Falls back to the state attribute set by StructuredLoggingMiddleware.
    """
    header_id = request.headers.get("x-request-id")
    if header_id:
        return header_id
    return getattr(request.state, "request_id", str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# T122 — Enhanced structured log entry with all required fields
# ---------------------------------------------------------------------------

def log_chat_response(
    request_id: str,
    query: str,
    mode: str,
    tone: Optional[str],
    chunks_retrieved: int,
    refused: bool,
    response_time_ms: int,
    user_id: Optional[str] = None,
    citation_count: int = 0,
    cached: bool = False,
):
    """
    T122 — Single structured log for a completed chat query.

    Includes all fields required by the observability spec:
    request_id, user_id, mode, tone, response_time_ms, chunks_retrieved,
    refused, citation_count, cached.
    """
    log_data = {
        "event": "chat_response",
        "request_id": request_id,
        "timestamp": time.time(),
        "user_id": user_id,
        "query_length": len(query),
        "mode": mode,
        "tone": tone or "neutral",
        "chunks_retrieved": chunks_retrieved,
        "citation_count": citation_count,
        "refused": refused,
        "response_time_ms": response_time_ms,
        "cached": cached,
    }
    logger.info(json.dumps(log_data))


# ---------------------------------------------------------------------------
# T123 — End-to-end RAG pipeline tracing
# ---------------------------------------------------------------------------

class PipelineTracer:
    """
    T123 — Lightweight span tracker for the RAG pipeline.

    Usage::

        tracer = PipelineTracer(request_id="…")
        tracer.start("embed")
        embedding = await embed_query(query)
        tracer.finish("embed")

        tracer.start("retrieve")
        chunks = await retrieve(embedding)
        tracer.finish("retrieve")

        tracer.log_summary()   # emits one JSON log with all span timings
    """

    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        self._spans: dict = {}
        self._order: list = []

    def start(self, stage: str) -> None:
        self._spans[stage] = {"start": time.monotonic(), "end": None, "duration_ms": None}
        self._order.append(stage)

    def finish(self, stage: str) -> float:
        if stage not in self._spans:
            return 0.0
        span = self._spans[stage]
        span["end"] = time.monotonic()
        span["duration_ms"] = round((span["end"] - span["start"]) * 1000, 2)
        return span["duration_ms"]

    def log_summary(self, mode: str = "", refused: bool = False) -> None:
        spans_summary = {
            stage: self._spans[stage]["duration_ms"]
            for stage in self._order
            if self._spans[stage]["duration_ms"] is not None
        }
        total_ms = sum(v for v in spans_summary.values() if v)
        log_data = {
            "event": "rag_pipeline_trace",
            "request_id": self.request_id,
            "timestamp": time.time(),
            "mode": mode,
            "refused": refused,
            "total_ms": round(total_ms, 2),
            "spans_ms": spans_summary,
        }
        logger.info(json.dumps(log_data))


def log_mode_boundary_violation(
    request_id: str,
    attempted_mode: str,
    reason: str,
):
    """
    Log when a mode boundary is violated (invalid mode requested).

    Args:
        request_id: Unique request identifier
        attempted_mode: The mode string that was rejected
        reason: Human-readable reason for rejection
    """
    log_data = {
        "event": "mode_boundary_violation",
        "request_id": request_id,
        "timestamp": time.time(),
        "attempted_mode": attempted_mode,
        "reason": reason,
    }
    logger.warning(json.dumps(log_data))


def log_selection_refusal(
    request_id: str,
    reason: str,
    selection_token_count: int,
    query: Optional[str] = None,
):
    """
    Log when a Selected-Text mode query is refused due to invalid selection.

    Args:
        request_id: Unique request identifier
        reason: Refusal reason (empty_selection | too_short | too_long | insufficient_context)
        selection_token_count: Token count of the selection that failed
        query: Optional query text
    """
    log_data = {
        "event": "selected_text_refusal",
        "request_id": request_id,
        "timestamp": time.time(),
        "mode": "selected_text",
        "refusal_reason": reason,
        "selection_token_count": selection_token_count,
        "vector_searches_performed": 0,
    }

    if query:
        log_data["query"] = query
        log_data["query_length"] = len(query)

    logger.warning(json.dumps(log_data))
