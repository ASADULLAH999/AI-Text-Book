"""
Infrastructure Verification Script
Tests all external services and configuration for Phase 2 completion.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List
import logging
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")
else:
    print(f"Warning: .env.local not found at {env_path}")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class InfrastructureVerifier:
    """Verify all infrastructure components."""

    def __init__(self):
        self.results: Dict[str, Dict] = {}

    async def verify_environment_variables(self) -> bool:
        """Verify required environment variables are set."""
        logger.info("\n" + "=" * 60)
        logger.info("1. Environment Variables")
        logger.info("=" * 60)

        required_vars = {
            "QDRANT_URL": "Qdrant Cloud URL",
            "QDRANT_API_KEY": "Qdrant API Key",
            "NEON_DATABASE_URL": "Neon Postgres URL",
            "OPENAI_API_KEY": "OpenAI API Key",
        }

        optional_vars = {
            "COHERE_API_KEY": "Cohere API Key (optional)",
            "UPSTASH_REDIS_URL": "Upstash Redis URL (optional)",
            "UPSTASH_REDIS_TOKEN": "Upstash Redis Token (optional)",
            "SENTRY_DSN": "Sentry DSN (optional)",
        }

        missing_required = []
        missing_optional = []

        # Check required variables
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                masked = value[:10] + "..." if len(value) > 10 else "***"
                logger.info(f"✓ {var}: {masked}")
            else:
                logger.error(f"✗ {var}: NOT SET")
                missing_required.append(var)

        # Check optional variables
        logger.info("\nOptional variables:")
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                masked = value[:10] + "..." if len(value) > 10 else "***"
                logger.info(f"✓ {var}: {masked}")
            else:
                logger.warning(f"⚠ {var}: NOT SET ({description})")
                missing_optional.append(var)

        success = len(missing_required) == 0

        self.results["environment"] = {
            "success": success,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
        }

        return success

    async def verify_qdrant(self) -> bool:
        """Verify Qdrant Cloud connection."""
        logger.info("\n" + "=" * 60)
        logger.info("2. Qdrant Vector Database")
        logger.info("=" * 60)

        try:
            from db.qdrant_client import qdrant_client

            # Test connection
            client = qdrant_client.get_client()
            logger.info(f"✓ Connected to Qdrant")

            # Get collection name
            collection_name = qdrant_client.get_collection_name()
            logger.info(f"  Collection: {collection_name}")

            # Check if collection exists
            await qdrant_client.ensure_collection_exists()
            logger.info(f"✓ Collection verified/created")

            # Get collection info
            try:
                collections = client.get_collections()
                collection_exists = any(c.name == collection_name for c in collections.collections)

                if collection_exists:
                    collection_info = client.get_collection(collection_name)
                    logger.info(f"  Vectors: {collection_info.vectors_count}")
                    logger.info(f"  Points: {collection_info.points_count}")
                else:
                    logger.info(f"  Collection is empty (ready for ingestion)")

            except Exception as e:
                logger.warning(f"Could not get collection details: {e}")

            self.results["qdrant"] = {"success": True}
            return True

        except Exception as e:
            logger.error(f"✗ Qdrant verification failed: {e}")
            self.results["qdrant"] = {"success": False, "error": str(e)}
            return False

    async def verify_postgres(self) -> bool:
        """Verify Neon Postgres connection."""
        logger.info("\n" + "=" * 60)
        logger.info("3. Neon Postgres Database")
        logger.info("=" * 60)

        try:
            from db.postgres_client import postgres_client

            # Test connection
            conn = await postgres_client.get_connection()
            logger.info(f"✓ Connected to Postgres")

            # Get database info
            query = "SELECT current_database(), current_user, version()"
            result = await postgres_client.execute_query(query)

            if result:
                info = result[0]
                logger.info(f"  Database: {info['current_database']}")
                logger.info(f"  User: {info['current_user']}")

            # Check for tables
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            tables_result = await postgres_client.execute_query(tables_query)

            if tables_result:
                tables = [row['table_name'] for row in tables_result]
                logger.info(f"  Tables: {', '.join(tables)}")

                # Check expected tables
                expected_tables = ["chunk_metadata", "query_logs", "analytics"]
                missing = set(expected_tables) - set(tables)

                if missing:
                    logger.warning(f"⚠ Missing tables: {missing}")
                    logger.info("  Run: python api/scripts/run_migrations.py")
                else:
                    logger.info(f"✓ All expected tables exist")
            else:
                logger.warning(f"⚠ No tables found (migrations not run)")
                logger.info("  Run: python api/scripts/run_migrations.py")

            self.results["postgres"] = {"success": True}
            return True

        except Exception as e:
            logger.error(f"✗ Postgres verification failed: {e}")
            self.results["postgres"] = {"success": False, "error": str(e)}
            return False

    async def verify_openai(self) -> bool:
        """Verify OpenAI API connection."""
        logger.info("\n" + "=" * 60)
        logger.info("4. OpenAI API")
        logger.info("=" * 60)

        try:
            from services.embedding_service import get_embedding_service

            # Get embedding service
            service = get_embedding_service()
            logger.info(f"✓ OpenAI client initialized")
            logger.info(f"  Model: {service.model}")

            # Test embedding generation
            logger.info("  Testing embedding generation...")
            test_text = "This is a test sentence for embedding."
            embedding = await service.embed_text(test_text)

            logger.info(f"✓ Generated embedding (dim: {len(embedding)})")

            self.results["openai"] = {"success": True}
            return True

        except Exception as e:
            logger.error(f"✗ OpenAI verification failed: {e}")
            self.results["openai"] = {"success": False, "error": str(e)}
            return False

    async def verify_optional_services(self) -> Dict[str, bool]:
        """Verify optional services."""
        logger.info("\n" + "=" * 60)
        logger.info("5. Optional Services")
        logger.info("=" * 60)

        results = {}

        # Cohere
        if os.getenv("COHERE_API_KEY"):
            try:
                import cohere
                co = cohere.Client(os.getenv("COHERE_API_KEY"))
                logger.info("✓ Cohere API configured")
                results["cohere"] = True
            except Exception as e:
                logger.warning(f"⚠ Cohere verification failed: {e}")
                results["cohere"] = False
        else:
            logger.info("⚠ Cohere API not configured (optional)")
            results["cohere"] = False

        # Upstash Redis
        if os.getenv("UPSTASH_REDIS_URL") and os.getenv("UPSTASH_REDIS_TOKEN"):
            logger.info("✓ Upstash Redis configured")
            results["upstash"] = True
        else:
            logger.info("⚠ Upstash Redis not configured (optional, rate limiting disabled)")
            results["upstash"] = False

        # Sentry
        if os.getenv("SENTRY_DSN"):
            logger.info("✓ Sentry configured")
            results["sentry"] = True
        else:
            logger.info("⚠ Sentry not configured (optional, error tracking disabled)")
            results["sentry"] = False

        self.results["optional"] = results
        return results

    async def verify_file_structure(self) -> bool:
        """Verify required files and directories exist."""
        logger.info("\n" + "=" * 60)
        logger.info("6. File Structure")
        logger.info("=" * 60)

        script_dir = Path(__file__).parent
        api_dir = script_dir.parent

        required_paths = {
            "Models": api_dir / "src" / "models",
            "Services": api_dir / "src" / "services",
            "Middleware": api_dir / "src" / "middleware",
            "Database": api_dir / "src" / "db",
            "Migrations": api_dir / "src" / "db" / "migrations",
            "Scripts": api_dir / "scripts",
            "Main App": api_dir / "src" / "main.py",
            "Requirements": api_dir / "requirements.txt",
            "Vercel Config": api_dir / "vercel.json",
        }

        missing = []

        for name, path in required_paths.items():
            if path.exists():
                logger.info(f"✓ {name}: {path.name}")
            else:
                logger.error(f"✗ {name}: NOT FOUND")
                missing.append(name)

        success = len(missing) == 0

        self.results["file_structure"] = {
            "success": success,
            "missing": missing,
        }

        return success

    def print_summary(self):
        """Print verification summary."""
        logger.info("\n" + "=" * 60)
        logger.info("INFRASTRUCTURE VERIFICATION SUMMARY")
        logger.info("=" * 60)

        all_passed = True

        # Core components
        core_components = ["environment", "qdrant", "postgres", "openai", "file_structure"]
        for component in core_components:
            if component in self.results:
                status = "✓ PASS" if self.results[component]["success"] else "✗ FAIL"
                logger.info(f"{component.upper()}: {status}")
                if not self.results[component]["success"]:
                    all_passed = False

        # Optional components
        if "optional" in self.results:
            logger.info("\nOptional Services:")
            for service, status in self.results["optional"].items():
                status_str = "✓ Configured" if status else "⚠ Not configured"
                logger.info(f"  {service.upper()}: {status_str}")

        logger.info("\n" + "=" * 60)
        if all_passed:
            logger.info("✓ ALL CORE INFRASTRUCTURE VERIFIED")
            logger.info("Ready to proceed with implementation!")
        else:
            logger.error("✗ INFRASTRUCTURE VERIFICATION FAILED")
            logger.error("Fix the issues above before proceeding")
        logger.info("=" * 60)

        return all_passed


async def main():
    """Main execution."""
    verifier = InfrastructureVerifier()

    # Run all verifications
    env_ok = await verifier.verify_environment_variables()
    file_ok = await verifier.verify_file_structure()
    qdrant_ok = await verifier.verify_qdrant()
    postgres_ok = await verifier.verify_postgres()
    openai_ok = await verifier.verify_openai()
    await verifier.verify_optional_services()

    # Print summary
    all_ok = verifier.print_summary()

    # Next steps
    if all_ok:
        logger.info("\nNext Steps:")
        logger.info("1. Run migrations: python api/scripts/run_migrations.py")
        logger.info("2. Ingest textbook: python api/scripts/ingest_pipeline.py")
        logger.info("3. Proceed to Phase 4: Core RAG Services")
    else:
        logger.error("\nFix the issues above before proceeding")

    return all_ok


if __name__ == "__main__":
    try:
        # Fix for Windows ProactorEventLoop
        if sys.platform == 'win32':
            import selectors
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
