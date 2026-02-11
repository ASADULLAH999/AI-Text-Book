"""
FastAPI Main Application
RAG-Powered Textbook Chatbot API
"""

import os
import logging
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
from middleware.auth_middleware import AuthMiddleware

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


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Docusaurus dev
        "http://localhost:8000",  # API dev
        os.getenv("FRONTEND_URL", ""),  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)


# Add custom middleware (order matters: last added = first executed)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(AuthMiddleware)


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
# Note: Routes will be added as they're implemented
# from routes.chat import router as chat_router
# from routes.chunks import router as chunks_router
# app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
# app.include_router(chunks_router, prefix="/api/v1", tags=["chunks"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
