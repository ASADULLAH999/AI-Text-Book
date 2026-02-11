"""
Neon Serverless Postgres Client
Manages connections to Neon Postgres for metadata and analytics storage.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
import psycopg
from psycopg import AsyncConnection
from psycopg.rows import dict_row
import logging

logger = logging.getLogger(__name__)


class PostgresClientSingleton:
    """Singleton wrapper for Postgres client with async connection pooling."""

    _connection: Optional[AsyncConnection] = None
    _connection_string: str = ""

    @classmethod
    async def get_connection(cls) -> AsyncConnection:
        """Get or create async Postgres connection."""
        if cls._connection is None or cls._connection.closed:
            try:
                cls._connection_string = os.getenv("NEON_DATABASE_URL")

                if not cls._connection_string:
                    raise ValueError("NEON_DATABASE_URL must be set")

                cls._connection = await psycopg.AsyncConnection.connect(
                    conninfo=cls._connection_string,
                    row_factory=dict_row,
                    autocommit=False,
                )

                logger.info("Connected to Neon Postgres")
            except Exception as e:
                logger.error(f"Failed to connect to Postgres: {e}")
                raise

        return cls._connection

    @classmethod
    async def execute_query(
        cls,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters (tuple)
            fetch: Whether to fetch and return results

        Returns:
            List of result rows (if fetch=True), None otherwise
        """
        conn = await cls.get_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                if fetch:
                    results = await cur.fetchall()
                    return results
                else:
                    await conn.commit()
                    return None
        except Exception as e:
            await conn.rollback()
            logger.error(f"Error executing query: {e}")
            raise

    @classmethod
    async def insert_chunk_metadata(
        cls,
        chunk_id: str,
        chapter: str,
        section: str,
        heading: str,
        word_count: int,
        file_path: str,
        **kwargs,
    ) -> bool:
        """Insert chunk metadata into the database."""
        query = """
            INSERT INTO chunk_metadata (
                chunk_id, chapter, section, heading, word_count, file_path,
                page_number, token_count, start_offset, end_offset, qdrant_point_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                chapter = EXCLUDED.chapter,
                section = EXCLUDED.section,
                heading = EXCLUDED.heading,
                word_count = EXCLUDED.word_count,
                updated_at = NOW()
        """
        params = (
            chunk_id,
            chapter,
            section,
            heading,
            word_count,
            file_path,
            kwargs.get("page_number"),
            kwargs.get("token_count"),
            kwargs.get("start_offset"),
            kwargs.get("end_offset"),
            kwargs.get("qdrant_point_id"),
        )

        try:
            await cls.execute_query(query, params, fetch=False)
            return True
        except Exception as e:
            logger.error(f"Error inserting chunk metadata: {e}")
            return False

    @classmethod
    async def log_query(
        cls,
        request_id: str,
        query: str,
        mode: str,
        model: str,
        latency_ms: int,
        **kwargs,
    ) -> bool:
        """Log a chatbot query for analytics."""
        sql = """
            INSERT INTO query_logs (
                request_id, query, mode, model, latency_ms,
                user_id, session_id, ip_address,
                chapter_filter, selected_text,
                chunks_retrieved, chunks_used, similarity_scores,
                temperature, response_length, tokens_used,
                embedding_latency_ms, retrieval_latency_ms, generation_latency_ms, citation_latency_ms,
                citations_count, confidence_avg,
                error_code, error_message,
                query_length
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        params = (
            request_id,
            query,
            mode,
            model,
            latency_ms,
            kwargs.get("user_id"),
            kwargs.get("session_id"),
            kwargs.get("ip_address"),
            kwargs.get("chapter_filter"),
            kwargs.get("selected_text"),
            kwargs.get("chunks_retrieved", 0),
            kwargs.get("chunks_used", 0),
            kwargs.get("similarity_scores"),
            kwargs.get("temperature"),
            kwargs.get("response_length"),
            kwargs.get("tokens_used"),
            kwargs.get("embedding_latency_ms"),
            kwargs.get("retrieval_latency_ms"),
            kwargs.get("generation_latency_ms"),
            kwargs.get("citation_latency_ms"),
            kwargs.get("citations_count", 0),
            kwargs.get("confidence_avg"),
            kwargs.get("error_code"),
            kwargs.get("error_message"),
            len(query),
        )

        try:
            await cls.execute_query(sql, params, fetch=False)
            return True
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            return False

    @classmethod
    async def get_analytics(
        cls,
        window_size: str = "1hour",
        limit: int = 24,
    ) -> List[Dict[str, Any]]:
        """Retrieve analytics data for a time window."""
        query = """
            SELECT *
            FROM analytics
            WHERE window_size = %s
            ORDER BY window_start DESC
            LIMIT %s
        """
        params = (window_size, limit)

        try:
            results = await cls.execute_query(query, params, fetch=True)
            return results or []
        except Exception as e:
            logger.error(f"Error retrieving analytics: {e}")
            return []

    @classmethod
    async def run_migrations(cls, migrations_dir: str) -> bool:
        """Run SQL migration files."""
        import glob

        try:
            migration_files = sorted(glob.glob(f"{migrations_dir}/*.sql"))

            for migration_file in migration_files:
                logger.info(f"Running migration: {migration_file}")
                with open(migration_file, "r") as f:
                    sql = f.read()
                    await cls.execute_query(sql, fetch=False)

            logger.info(f"Successfully ran {len(migration_files)} migrations")
            return True
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False

    @classmethod
    async def close(cls):
        """Close the Postgres connection."""
        if cls._connection and not cls._connection.closed:
            await cls._connection.close()
            cls._connection = None
            logger.info("Closed Postgres connection")


# Export singleton instance
postgres_client = PostgresClientSingleton()
