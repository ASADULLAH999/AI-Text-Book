"""
Authentication Middleware
Optional JWT validation for rate limit tier determination.
"""

import os
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Optional authentication middleware for JWT validation."""

    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    async def dispatch(self, request: Request, call_next):
        """Extract and validate JWT if present."""
        # Skip auth for health checks
        if request.url.path in ["/api/v1/health", "/health"]:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix

            try:
                # Decode and validate JWT
                user = await self._validate_token(token)
                if user:
                    request.state.user = user
                    logger.info(f"Authenticated user: {user.get('id')}")
            except Exception as e:
                logger.warning(f"JWT validation failed: {e}")
                # Don't block request on auth failure (optional auth)

        # Continue processing
        return await call_next(request)

    async def _validate_token(self, token: str) -> Optional[dict]:
        """
        Validate JWT token.

        Returns:
            User dictionary if valid, None otherwise
        """
        if not self.jwt_secret:
            logger.warning("JWT_SECRET not configured, skipping validation")
            return None

        try:
            import jwt

            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
            )

            # Extract user information
            user = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "is_premium": payload.get("is_premium", False),
            }

            return user

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating JWT: {e}")
            return None


def require_auth(request: Request):
    """
    Dependency to require authentication for specific endpoints.

    Usage:
        @app.get("/protected", dependencies=[Depends(require_auth)])
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def require_admin(request: Request):
    """
    Dependency to require admin privileges.

    Usage:
        @app.get("/admin", dependencies=[Depends(require_admin)])
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
