#!/usr/bin/env python3
"""
Neon Serverless Postgres Provisioning Script

This script validates and sets up the Neon Postgres database for the RAG chatbot.
Database specifications:
- Provider: Neon Serverless Postgres
- Tables: conversations, messages, citations, feedback, analytics
- SSL mode: Required
- Connection pooling: Enabled

Usage:
    python provision_neon.py --check      # Check database connection
    python provision_neon.py --init       # Initialize database schema
    python provision_neon.py --migrate    # Run migrations
    python provision_neon.py --status     # Show database status

Environment variables required:
    DATABASE_URL: Full Postgres connection string
    OR individual components:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

import argparse
import os
import sys
from typing import Dict, Any, Optional

try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_database_url() -> str:
    """Get database URL from environment variables."""
    # Try DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Construct from individual components
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    sslmode = os.getenv("POSTGRES_SSL_MODE", "require")

    if not all([host, dbname, user, password]):
        print("ERROR: Database connection parameters not set")
        print("Set DATABASE_URL or all of: POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD")
        sys.exit(1)

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"


def get_connection():
    """Create a database connection."""
    database_url = get_database_url()
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to database: {e}")
        sys.exit(1)


def check_connection() -> bool:
    """Check if database connection is successful."""
    try:
        print("\n🔌 Testing database connection...")
        conn = get_connection()
        cur = conn.cursor()

        # Test query
        cur.execute("SELECT version();")
        version_result = cur.fetchone()
        version = version_result[0] if version_result else "Unknown"

        # Get database name
        cur.execute("SELECT current_database();")
        dbname_result = cur.fetchone()
        dbname = dbname_result[0] if dbname_result else "Unknown"

        # Get connection info
        cur.execute("SELECT inet_server_addr(), inet_server_port();")
        server_info = cur.fetchone()

        cur.close()
        conn.close()

        print(f"✅ Connection successful!")
        print(f"   Database: {dbname}")
        if server_info:
            print(f"   Server: {server_info[0] or 'localhost'}:{server_info[1]}")
        print(f"   Version: {version[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def get_database_status() -> Dict[str, Any]:
    """Get detailed database status information."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        status = {}

        # Database size
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size;
        """)
        size_result = cur.fetchone()
        status["database_size"] = size_result[0] if size_result else "Unknown"

        # Table count
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        count_result = cur.fetchone()
        status["table_count"] = count_result[0] if count_result else 0

        # List tables with row counts
        cur.execute("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        status["tables"] = [
            {"schema": t[0], "name": t[1], "size": t[2]}
            for t in tables
        ]

        # Connection info
        cur.execute("SELECT current_user, current_database(), inet_server_addr();")
        conn_info = cur.fetchone()
        if conn_info:
            status["user"] = conn_info[0]
            status["database"] = conn_info[1]
            status["host"] = conn_info[2] or "localhost"
        else:
            status["user"] = "Unknown"
            status["database"] = "Unknown"
            status["host"] = "localhost"

        # Neon-specific: Check if extensions are available
        cur.execute("""
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname IN ('pg_stat_statements', 'pg_trgm', 'pgcrypto');
        """)
        extensions = cur.fetchall()
        status["extensions"] = [{"name": e[0], "version": e[1]} for e in extensions]

        cur.close()
        conn.close()

        return status

    except Exception as e:
        print(f"❌ ERROR: Failed to get database status: {e}")
        return {}


def print_database_status(status: Dict[str, Any]) -> None:
    """Pretty print database status."""
    if not status:
        print("⚠️  Unable to retrieve database status")
        return

    print("\n📊 Database Status")
    print(f"   User: {status.get('user', 'unknown')}")
    print(f"   Database: {status.get('database', 'unknown')}")
    print(f"   Host: {status.get('host', 'unknown')}")
    print(f"   Size: {status.get('database_size', 'unknown')}")
    print(f"   Tables: {status.get('table_count', 0)}")

    if status.get("tables"):
        print("\n   📋 Tables:")
        for table in status["tables"]:
            print(f"      - {table['name']} ({table['size']})")

    if status.get("extensions"):
        print("\n   🔌 Extensions:")
        for ext in status["extensions"]:
            print(f"      - {ext['name']} v{ext['version']}")


def check_schema_exists() -> bool:
    """Check if required tables exist."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        required_tables = ['conversations', 'messages', 'citations', 'feedback']

        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = ANY(%s);
        """, (required_tables,))

        existing_tables = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        missing_tables = set(required_tables) - set(existing_tables)

        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            return False

        print(f"\n✅ All required tables exist: {', '.join(required_tables)}")
        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to check schema: {e}")
        return False


def initialize_schema() -> bool:
    """Initialize database schema by running migrations."""
    try:
        print("\n🔧 Initializing database schema...")

        # Import and run migrations
        import subprocess
        result = subprocess.run(
            ["python", "api/scripts/run_migrations.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Database schema initialized successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Schema initialization failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ ERROR: Failed to initialize schema: {e}")
        return False


def run_migrations() -> bool:
    """Run database migrations."""
    try:
        print("\n🔄 Running database migrations...")

        import subprocess
        result = subprocess.run(
            ["python", "api/scripts/run_migrations.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Migrations failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ ERROR: Failed to run migrations: {e}")
        return False


def create_setup_instructions():
    """Print Neon setup instructions."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Neon Serverless Postgres Setup Instructions                  ║
╚════════════════════════════════════════════════════════════════╝

📝 Step-by-step guide:

1. Create a Neon account:
   → Visit: https://console.neon.tech/signup
   → Sign up with GitHub or email

2. Create a new project:
   → Click "Create Project"
   → Name: "ai-textbook-rag"
   → Region: Choose closest to your users
   → Postgres version: 15 or higher

3. Get connection string:
   → Navigate to your project dashboard
   → Click "Connection Details"
   → Copy the connection string (it looks like):
     postgresql://user:pass@ep-xxxxx.region.aws.neon.tech/dbname

4. Configure environment:
   → Copy .env.template to .env
   → Set DATABASE_URL with your connection string
   → Ensure ?sslmode=require is appended

5. Initialize the database:
   → Run: python api/scripts/provision_neon.py --init

6. Verify setup:
   → Run: python api/scripts/provision_neon.py --check
   → Run: python api/scripts/provision_neon.py --status

💡 Neon Features:
   - Auto-scaling: Automatically scales with load
   - Branching: Create database branches for testing
   - Point-in-time recovery: Restore to any point in last 7 days
   - Connection pooling: Built-in with PgBouncer

📚 Documentation: https://neon.tech/docs/introduction

⚠️  Important Notes:
   - Free tier: 3 GB storage, 100 compute hours/month
   - SSL is required for all connections
   - Use connection pooling for serverless functions
   - Enable auto-suspend to save compute hours
""")


def main():
    parser = argparse.ArgumentParser(
        description="Provision Neon Serverless Postgres for RAG chatbot"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Check database connection",
    )
    group.add_argument(
        "--init",
        action="store_true",
        help="Initialize database schema",
    )
    group.add_argument(
        "--migrate",
        action="store_true",
        help="Run database migrations",
    )
    group.add_argument(
        "--status",
        action="store_true",
        help="Show detailed database status",
    )
    group.add_argument(
        "--setup-guide",
        action="store_true",
        help="Show Neon setup instructions",
    )

    args = parser.parse_args()

    if args.setup_guide:
        create_setup_instructions()
        sys.exit(0)

    # Execute requested action
    if args.check:
        success = check_connection()
        if success:
            check_schema_exists()
        sys.exit(0 if success else 1)

    elif args.init:
        if not check_connection():
            sys.exit(1)
        success = initialize_schema()
        sys.exit(0 if success else 1)

    elif args.migrate:
        if not check_connection():
            sys.exit(1)
        success = run_migrations()
        sys.exit(0 if success else 1)

    elif args.status:
        if not check_connection():
            sys.exit(1)
        status = get_database_status()
        print_database_status(status)
        sys.exit(0 if status else 1)


if __name__ == "__main__":
    main()
