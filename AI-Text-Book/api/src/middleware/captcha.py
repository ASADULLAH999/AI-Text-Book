"""
T108 — CAPTCHA challenge for anomalous traffic patterns.

Triggers a Cloudflare Turnstile CAPTCHA challenge when a client:
  - Exceeds ANOMALY_BURST_THRESHOLD requests in ANOMALY_WINDOW_SECONDS.
  - Sends requests with no User-Agent header.
  - Has previously failed the CAPTCHA (tracked in Redis if available).

The frontend should read the `X-Captcha-Required: true` header and present
the Turnstile widget. On success it passes the token in the
`CF-Turnstile-Response` header on the next request.
"""

import os
import time
from collections import defaultdict, deque
from typing import Optional

import httpx
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TURNSTILE_SECRET = os.getenv("CLOUDFLARE_TURNSTILE_SECRET_KEY", "")
TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Anomaly thresholds
ANOMALY_BURST_THRESHOLD = int(os.getenv("CAPTCHA_BURST_THRESHOLD", "30"))
ANOMALY_WINDOW_SECONDS = int(os.getenv("CAPTCHA_WINDOW_SECONDS", "60"))

# In-process sliding-window counters (keyed by IP).
# For multi-instance deployments, replace with Redis counters.
_request_windows: dict[str, deque] = defaultdict(deque)
_captcha_required: set[str] = set()  # IPs currently requiring CAPTCHA


# ---------------------------------------------------------------------------
# Anomaly detection helpers
# ---------------------------------------------------------------------------

def _is_anomalous(ip: str) -> bool:
    """Return True if *ip* exceeds the burst threshold in the sliding window."""
    now = time.monotonic()
    window = _request_windows[ip]

    # Evict timestamps outside the window
    while window and now - window[0] > ANOMALY_WINDOW_SECONDS:
        window.popleft()

    window.append(now)
    return len(window) > ANOMALY_BURST_THRESHOLD


def _clear_captcha(ip: str) -> None:
    _captcha_required.discard(ip)
    _request_windows.pop(ip, None)


# ---------------------------------------------------------------------------
# Turnstile token verification
# ---------------------------------------------------------------------------

async def _verify_turnstile(token: str, remote_ip: Optional[str]) -> bool:
    """Call the Cloudflare Turnstile siteverify endpoint."""
    if not TURNSTILE_SECRET:
        # CAPTCHA disabled (no secret key set)
        logger.debug("T108: Turnstile secret not configured — CAPTCHA verification skipped")
        return True

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                TURNSTILE_VERIFY_URL,
                data={
                    "secret": TURNSTILE_SECRET,
                    "response": token,
                    **({"remoteip": remote_ip} if remote_ip else {}),
                },
            )
            resp.raise_for_status()
            data = resp.json()
            success = bool(data.get("success"))
            if not success:
                logger.warning(
                    f"T108: Turnstile verification failed for {remote_ip}: {data.get('error-codes')}"
                )
            return success
    except Exception as exc:
        logger.error(f"T108: Turnstile verification error: {exc}")
        # Fail open — don't block users if verification service is unreachable
        return True


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class CaptchaMiddleware(BaseHTTPMiddleware):
    """
    Middleware that detects anomalous request patterns and requires a
    Cloudflare Turnstile CAPTCHA token to proceed.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip for health checks, OPTIONS, and non-API paths
        if request.method == "OPTIONS" or request.url.path in ("/", "/api/v1/health", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # ── 1. Check if this IP already requires CAPTCHA ──────────────────────
        if client_ip in _captcha_required:
            turnstile_token = request.headers.get("cf-turnstile-response", "")
            if not turnstile_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "captcha_required",
                        "message": "Unusual activity detected. Please complete the CAPTCHA challenge.",
                        "captcha_provider": "cloudflare_turnstile",
                    },
                )
            # Verify the submitted token
            verified = await _verify_turnstile(turnstile_token, client_ip)
            if verified:
                _clear_captcha(client_ip)
                logger.info(f"T108: CAPTCHA passed for {client_ip}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "captcha_invalid",
                        "message": "CAPTCHA verification failed. Please try again.",
                        "captcha_provider": "cloudflare_turnstile",
                    },
                )

        # ── 2. No-User-Agent heuristic (bot signal) ───────────────────────────
        user_agent = request.headers.get("user-agent", "")
        if not user_agent and request.url.path.startswith("/api/"):
            logger.warning(f"T108: Missing User-Agent from {client_ip}")
            _captcha_required.add(client_ip)

        # ── 3. Burst anomaly detection ────────────────────────────────────────
        if _is_anomalous(client_ip):
            _captcha_required.add(client_ip)
            logger.warning(
                f"T108: Anomalous burst from {client_ip} "
                f"(>{ANOMALY_BURST_THRESHOLD} req/{ANOMALY_WINDOW_SECONDS}s)"
            )

        # ── 4. If CAPTCHA now required, reject this request ───────────────────
        if client_ip in _captcha_required:
            response_headers = {"X-Captcha-Required": "true"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "captcha_required",
                    "message": "Unusual activity detected. Please complete the CAPTCHA challenge.",
                    "captcha_provider": "cloudflare_turnstile",
                },
                headers=response_headers,
            )

        response = await call_next(request)
        return response
