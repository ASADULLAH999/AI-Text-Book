"""
FastAPI Main Application
RAG-Powered Textbook Chatbot API
"""

import os
import sys
import logging

# Load .env before any other imports so os.getenv() calls see the values.
# Resolve path relative to this file: api/src/../.env → api/.env
from dotenv import load_dotenv
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_ENV_PATH, override=False)

# Ensure api/src/ is on the path so flat imports (middleware, db, services)
# resolve correctly regardless of the working directory.
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Import middleware
from middleware.logger import StructuredLoggingMiddleware
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.request_validator import RequestValidatorMiddleware
from middleware.error_handler import ErrorHandlerMiddleware
from middleware.captcha import CaptchaMiddleware
from middleware.request_signing import RequestSigningMiddleware

# Import database clients
from db.qdrant_client import qdrant_client
from db.postgres_client import postgres_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# Initialize Sentry
def init_sentry():
    """Initialize Sentry error tracking."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    sentry_environment = os.getenv("SENTRY_ENVIRONMENT", "development")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=sentry_environment,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR,
                ),
            ],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0")),
        )
        logger.info(f"Sentry initialized for environment: {sentry_environment}")
    else:
        logger.warning("Sentry DSN not configured, error tracking disabled")


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting RAG Chatbot API...")
    init_sentry()

    # Initialize database connections
    try:
        await qdrant_client.ensure_collection_exists()
        logger.info("Qdrant collection verified")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")

    try:
        await postgres_client.get_connection()
        logger.info("Postgres connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Postgres: {e}")

    logger.info("API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot API...")
    qdrant_client.close()
    await postgres_client.close()
    logger.info("API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Textbook RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for textbook content",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)


# T111 — CORS configuration with production domains
# Allowed origins are sourced from env to avoid hardcoding domains.
_CORS_ALLOWED_ORIGINS: list[str] = list(filter(None, [
    "http://localhost:3000",        # Docusaurus dev server
    "http://localhost:3001",        # Docusaurus production serve
    "http://localhost:3002",        # Docusaurus production serve (alt port)
    "http://localhost:8000",        # API dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    os.getenv("FRONTEND_URL"),      # Primary production frontend
    os.getenv("FRONTEND_URL_ALT"),  # Alternate / preview URL (e.g. Vercel preview)
    os.getenv("CORS_ORIGIN_1"),     # Additional origins if needed
    os.getenv("CORS_ORIGIN_2"),
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "CF-Turnstile-Response",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Captcha-Required",
    ],
    max_age=600,
)


# Add custom middleware (order matters: last added = first executed)
# Error handler wraps everything
app.add_middleware(ErrorHandlerMiddleware)
# Request validator before business logic
app.add_middleware(RequestValidatorMiddleware)
# CAPTCHA challenge for anomalous traffic (T108)
app.add_middleware(CaptchaMiddleware)
# Request signing verification (T112)
app.add_middleware(RequestSigningMiddleware)
# Structured logging and rate limiting
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )

    # Report to Sentry
    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
        },
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Textbook RAG Chatbot API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/api/v1/docs",
    }


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Qdrant connection
        qdrant_healthy = True
        try:
            qdrant_client.get_client()
        except Exception:
            qdrant_healthy = False

        # Check Postgres connection
        postgres_healthy = True
        try:
            await postgres_client.get_connection()
        except Exception:
            postgres_healthy = False

        # Overall health
        healthy = qdrant_healthy and postgres_healthy

        return {
            "status": "healthy" if healthy else "degraded",
            "version": "1.0.0",
            "services": {
                "qdrant": "healthy" if qdrant_healthy else "unhealthy",
                "postgres": "healthy" if postgres_healthy else "unhealthy",
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
            },
        )


# Import and include routers
from api.v1.chat import router as chat_router

# Include routers
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
