"""
Rate Limiting Middleware
Implements rate limiting using Upstash Redis with tiered limits.
"""

import os
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
import logging

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Upstash Redis."""

    def __init__(self, app):
        super().__init__(app)
        self.redis_url = os.getenv("UPSTASH_REDIS_URL")
        self.redis_token = os.getenv("UPSTASH_REDIS_TOKEN")

        # Rate limit tiers (requests per hour)
        self.rate_limits = {
            "anonymous": int(os.getenv("CHATBOT_RATE_LIMIT_ANONYMOUS", "10")),
            "authenticated": int(os.getenv("CHATBOT_RATE_LIMIT_AUTHENTICATED", "100")),
            "premium": int(os.getenv("CHATBOT_RATE_LIMIT_PREMIUM", "1000")),
        }

        # Burst allowance (2x for 10 seconds)
        self.burst_multiplier = 2
        self.burst_window = 10

    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request."""
        # Skip rate limiting for health checks
        if request.url.path in ["/api/v1/health", "/health"]:
            return await call_next(request)

        # Skip if Redis not configured (development mode)
        if not self.redis_url or not self.redis_token:
            logger.warning("Rate limiting disabled: Redis not configured")
            return await call_next(request)

        # Get user tier and identifier
        user_tier = self._get_user_tier(request)
        user_id = self._get_user_identifier(request)

        # Check rate limit
        try:
            is_allowed, remaining, reset_time = await self._check_rate_limit(
                user_id=user_id,
                tier=user_tier,
            )

            if not is_allowed:
                # Return 429 Too Many Requests
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded. Allowed: {self.rate_limits[user_tier]} requests/hour",
                        "tier": user_tier,
                        "remaining": remaining,
                        "reset_at": reset_time,
                    },
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.rate_limits[user_tier])
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request on rate limiter failure (fail open)
            return await call_next(request)

    def _get_user_tier(self, request: Request) -> str:
        """Determine user tier from request."""
        # Check for authentication
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return "anonymous"

        # Check user attributes (would come from JWT or user service)
        # For now, default to authenticated
        user = getattr(request.state, "user", None)
        if user and user.get("is_premium"):
            return "premium"
        elif user:
            return "authenticated"

        return "anonymous"

    def _get_user_identifier(self, request: Request) -> str:
        """Get unique identifier for the user."""
        # Try to get user ID from auth
        user = getattr(request.state, "user", None)
        if user and user.get("id"):
            return f"user:{user['id']}"

        # Fall back to IP address for anonymous users
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    async def _check_rate_limit(
        self,
        user_id: str,
        tier: str,
    ) -> tuple[bool, int, int]:
        """
        Check rate limit using Upstash Redis.

        Returns:
            (is_allowed, remaining_requests, reset_timestamp)
        """
        current_time = int(time.time())
        window_key = f"ratelimit:{user_id}:hour:{current_time // 3600}"
        burst_key = f"ratelimit:{user_id}:burst:{current_time // self.burst_window}"

        limit = self.rate_limits[tier]
        burst_limit = limit * self.burst_multiplier

        try:
            async with httpx.AsyncClient() as client:
                # Increment hourly counter
                response = await client.post(
                    f"{self.redis_url}/incr/{window_key}",
                    headers={"Authorization": f"Bearer {self.redis_token}"},
                )
                response.raise_for_status()
                hourly_count = response.json()["result"]

                # Set expiry on first request (3600 seconds = 1 hour)
                if hourly_count == 1:
                    await client.post(
                        f"{self.redis_url}/expire/{window_key}/3600",
                        headers={"Authorization": f"Bearer {self.redis_token}"},
                    )

                # Increment burst counter
                burst_response = await client.post(
                    f"{self.redis_url}/incr/{burst_key}",
                    headers={"Authorization": f"Bearer {self.redis_token}"},
                )
                burst_response.raise_for_status()
                burst_count = burst_response.json()["result"]

                # Set expiry on burst counter
                if burst_count == 1:
                    await client.post(
                        f"{self.redis_url}/expire/{burst_key}/{self.burst_window}",
                        headers={"Authorization": f"Bearer {self.redis_token}"},
                    )

                # Check both hourly and burst limits
                hourly_allowed = hourly_count <= limit
                burst_allowed = burst_count <= burst_limit

                is_allowed = hourly_allowed and burst_allowed
                remaining = max(0, limit - hourly_count)
                reset_time = ((current_time // 3600) + 1) * 3600

                if not is_allowed:
                    logger.warning(
                        f"Rate limit exceeded for {user_id} (tier: {tier}). "
                        f"Hourly: {hourly_count}/{limit}, Burst: {burst_count}/{burst_limit}"
                    )

                return is_allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open: allow request on error
            return True, limit, current_time + 3600
