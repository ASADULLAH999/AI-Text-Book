"""
Run Database Migrations
Executes all SQL migration files against Neon Postgres database.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional  # Fix: Add Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from db.postgres_client import postgres_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def run_all_migrations(migrations_dir: Optional[str] = None) -> bool:  # Fix: Optional type
    """
    Run all migration files in order.

    Args:
        migrations_dir: Path to migrations directory

    Returns:
        True if all migrations succeeded
    """
    # Fix: Proper type handling
    if migrations_dir is None:
        # Default to src/db/migrations
        script_dir = Path(__file__).parent
        migrations_path = script_dir.parent / "src" / "db" / "migrations"
    else:
        migrations_path = Path(migrations_dir)

    if not migrations_path.exists():
        logger.error(f"Migrations directory not found: {migrations_path}")
        return False

    logger.info(f"Running migrations from: {migrations_path}")

    # Get all .sql files sorted by name
    migration_files = sorted(migrations_path.glob("*.sql"))

    if not migration_files:
        logger.warning("No migration files found")
        return True

    logger.info(f"Found {len(migration_files)} migration files")

    # Execute each migration
    for migration_file in migration_files:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Executing: {migration_file.name}")
        logger.info(f"{'=' * 60}")

        try:
            # Read migration file
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            # Execute migration
            await postgres_client.execute_query(sql, fetch=False)

            logger.info(f"✓ {migration_file.name} completed successfully")

        except Exception as e:
            logger.error(f"✗ {migration_file.name} failed: {e}")
            return False

    logger.info(f"\n{'=' * 60}")
    logger.info(f"All migrations completed successfully")
    logger.info(f"{'=' * 60}")

    return True


async def verify_tables() -> bool:
    """
    Verify that all expected tables exist.

    Returns:
        True if verification passed
    """
    logger.info("\nVerifying database schema...")

    expected_tables = [
        "chunk_metadata",
        "query_logs",
        "analytics",
    ]

    try:
        # Query for existing tables
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """

        result = await postgres_client.execute_query(query)

        if not result:
            logger.error("No tables found in database")
            return False

        existing_tables = [row['table_name'] for row in result]

        logger.info(f"Found tables: {existing_tables}")

        # Check for expected tables
        missing_tables = set(expected_tables) - set(existing_tables)
        extra_tables = set(existing_tables) - set(expected_tables)

        if missing_tables:
            logger.error(f"Missing expected tables: {missing_tables}")
            return False

        if extra_tables:
            logger.info(f"Additional tables present: {extra_tables}")

        logger.info("✓ All expected tables exist")

        # Get table row counts
        logger.info("\nTable statistics:")
        for table in expected_tables:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            count_result = await postgres_client.execute_query(count_query)
            count = count_result[0]['count'] if count_result else 0
            logger.info(f"  {table}: {count} rows")

        return True

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


async def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection successful
    """
    logger.info("Testing database connection...")

    try:
        conn = await postgres_client.get_connection()

        # Simple query to verify connection
        query = "SELECT version(), current_database(), current_user"
        result = await postgres_client.execute_query(query)

        if result:
            info = result[0]
            logger.info(f"✓ Connected to: {info['current_database']}")
            logger.info(f"  User: {info['current_user']}")
            logger.info(f"  Version: {info['version'][:50]}...")
            return True

        return False

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--migrations-dir",
        type=str,
        help="Path to migrations directory (default: api/src/db/migrations)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify tables, don't run migrations",
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection before running migrations",
    )

    args = parser.parse_args()

    async def run():
        """Async main function."""
        # Test connection first if requested
        if args.test_connection or not args.verify_only:
            connection_ok = await test_connection()
            if not connection_ok:
                logger.error("Database connection failed. Check your NEON_DATABASE_URL")
                return False

        # Run migrations or verify only
        if args.verify_only:
            verification_passed = await verify_tables()
            return verification_passed
        else:
            migrations_ok = await run_all_migrations(args.migrations_dir)
            if not migrations_ok:
                return False

            # Verify after migrations
            verification_passed = await verify_tables()
            return verification_passed

    try:
        # Fix for Windows ProactorEventLoop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        success = asyncio.run(run())

        if success:
            logger.info("\n" + "=" * 60)
            logger.info("Database setup complete!")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("\n" + "=" * 60)
            logger.error("Database setup failed")
            logger.error("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
