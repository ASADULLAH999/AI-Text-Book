"""
Quick Import Verification Test
Tests that all module imports resolve correctly.
"""

import sys
from pathlib import Path

# Add src to path (same pattern as other scripts)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")

    try:
        # Database imports
        from db.postgres_client import postgres_client
        print("✓ db.postgres_client")

        from db.qdrant_client import qdrant_client
        print("✓ db.qdrant_client")

        # Service imports
        from services.embedding_service import get_embedding_service
        print("✓ services.embedding_service")

        # Middleware imports
        from middleware.logger import StructuredLoggingMiddleware
        print("✓ middleware.logger")

        from middleware.rate_limiter import RateLimiterMiddleware
        print("✓ middleware.rate_limiter")

        from middleware.auth_middleware import AuthMiddleware
        print("✓ middleware.auth_middleware")

        # Model imports
        from models.chunk import Chunk
        print("✓ models.chunk")

        from models.chat_request import ChatRequest
        print("✓ models.chat_request")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
