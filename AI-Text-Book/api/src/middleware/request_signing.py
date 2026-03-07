"""
T112 — HMAC-SHA256 request signing for API authentication.

How it works:
  - The client computes an HMAC-SHA256 signature over:
      Method + "\n" + Path + "\n" + Timestamp + "\n" + BodyHash
    using a shared secret (API_SIGNING_SECRET env var).
  - The signature and timestamp are sent in headers:
      X-Signature: <hex-digest>
      X-Timestamp: <unix-epoch-seconds>
  - The server recomputes the signature and rejects mismatches.
  - Replays older than SIGNATURE_TTL_SECONDS are rejected.

This middleware is opt-in and only enforced when API_SIGNING_SECRET is set.
Set ENFORCE_REQUEST_SIGNING=true to enable in production.
"""

import hashlib
import hmac
import os
import time
from typing import Optional

import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Configuration
_SIGNING_SECRET: str = os.getenv("API_SIGNING_SECRET", "")
_ENFORCE: bool = os.getenv("ENFORCE_REQUEST_SIGNING", "false").lower() == "true"
_SIGNATURE_TTL_SECONDS: int = int(os.getenv("SIGNATURE_TTL_SECONDS", "300"))  # 5 minutes

# Paths that DO NOT require signing (public, read-only)
_UNSIGNED_PATHS = frozenset({
    "/",
    "/api/v1/health",
    "/health",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
})


def _compute_signature(
    method: str,
    path: str,
    timestamp: str,
    body: bytes,
    secret: str,
) -> str:
    """
    Compute the expected HMAC-SHA256 signature.

    The signed string is:
        {METHOD}\\n{path}\\n{timestamp}\\n{sha256(body)}
    """
    body_hash = hashlib.sha256(body).hexdigest()
    signed_string = f"{method.upper()}\n{path}\n{timestamp}\n{body_hash}"
    return hmac.new(
        secret.encode("utf-8"),
        signed_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class RequestSigningMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify HMAC-SHA256 request signatures.

    Only active when both:
      - API_SIGNING_SECRET is set, AND
      - ENFORCE_REQUEST_SIGNING=true (or the path requires it)
    """

    async def dispatch(self, request: Request, call_next):
        if not _SIGNING_SECRET or not _ENFORCE:
            return await call_next(request)

        # Skip unsigned paths and OPTIONS
        if request.method == "OPTIONS" or request.url.path in _UNSIGNED_PATHS:
            return await call_next(request)

        # Extract signature headers
        signature = request.headers.get("x-signature", "")
        timestamp_str = request.headers.get("x-timestamp", "")

        if not signature or not timestamp_str:
            logger.warning(
                f"T112: Missing signature headers from {request.client.host if request.client else '?'}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "signature_required",
                    "message": "Request signature required. Include X-Signature and X-Timestamp headers.",
                },
            )

        # Reject stale timestamps (replay protection)
        try:
            ts = int(timestamp_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "invalid_timestamp", "message": "X-Timestamp must be a Unix epoch integer."},
            )

        age = abs(time.time() - ts)
        if age > _SIGNATURE_TTL_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "signature_expired",
                    "message": f"Request timestamp is too old ({int(age)}s). Maximum: {_SIGNATURE_TTL_SECONDS}s.",
                },
            )

        # Read body (buffered so handlers can still read it)
        body = await request.body()

        # Compute expected signature
        expected = _compute_signature(
            method=request.method,
            path=request.url.path,
            timestamp=timestamp_str,
            body=body,
            secret=_SIGNING_SECRET,
        )

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(signature.lower(), expected.lower()):
            logger.warning(
                f"T112: Signature mismatch for {request.method} {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_signature", "message": "Request signature is invalid."},
            )

        return await call_next(request)


# ---------------------------------------------------------------------------
# Client-side helper (for use in tests and SDK)
# ---------------------------------------------------------------------------

def sign_request(
    method: str,
    path: str,
    body: bytes,
    secret: str,
    timestamp: Optional[int] = None,
) -> dict[str, str]:
    """
    Generate X-Signature and X-Timestamp headers for a request.

    Usage (Python client)::

        import httpx, time
        from middleware.request_signing import sign_request

        body = b'{"message": "hello"}'
        headers = sign_request("POST", "/api/v1/chat", body, secret=MY_SECRET)
        httpx.post("/api/v1/chat", content=body, headers=headers)
    """
    ts = str(timestamp or int(time.time()))
    sig = _compute_signature(method, path, ts, body, secret)
    return {"x-signature": sig, "x-timestamp": ts}
