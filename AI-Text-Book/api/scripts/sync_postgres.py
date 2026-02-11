"""
Sync Postgres Metadata Script
Syncs chunk metadata from JSON to Postgres for audit trail and analytics.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from db.postgres_client import postgres_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def sync_chunk_metadata(
    chunks_file: str,
    batch_size: int = 100,
) -> int:
    """
    Sync chunk metadata to Postgres.

    Args:
        chunks_file: Path to chunks JSON file
        batch_size: Number of chunks to process per batch

    Returns:
        Number of chunks synced
    """
    # Load chunks
    logger.info(f"Loading chunks from: {chunks_file}")
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks")

    # Sync metadata
    total_synced = 0
    batch_count = (len(chunks) + batch_size - 1) // batch_size

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = i // batch_size + 1

        logger.info(f"Syncing batch {batch_num}/{batch_count} ({len(batch)} chunks)...")

        for chunk in batch:
            try:
                success = await postgres_client.insert_chunk_metadata(
                    chunk_id=chunk["chunk_id"],
                    chapter=chunk["metadata"]["chapter"],
                    section=chunk["metadata"]["section"],
                    heading=chunk["metadata"].get("heading", "Unknown"),
                    word_count=chunk["word_count"],
                    file_path=chunk["metadata"]["file_path"],
                    page_number=chunk["metadata"].get("page_number"),
                    token_count=chunk.get("char_count"),  # Using char_count as proxy
                )

                if success:
                    total_synced += 1

            except Exception as e:
                logger.error(f"Error syncing chunk {chunk['chunk_id']}: {e}")
                # Continue with other chunks

        logger.info(f"Batch {batch_num} synced ({total_synced} total)")

    logger.info(f"Successfully synced {total_synced} chunk metadata records")
    return total_synced


async def verify_sync(sample_size: int = 10) -> bool:
    """
    Verify metadata sync by checking database.

    Args:
        sample_size: Number of records to check

    Returns:
        True if verification passed
    """
    logger.info("Verifying metadata sync...")

    try:
        # Query recent records
        query = """
            SELECT COUNT(*) as total_count,
                   COUNT(DISTINCT chapter) as unique_chapters,
                   COUNT(DISTINCT section) as unique_sections
            FROM chunk_metadata
        """

        result = await postgres_client.execute_query(query)

        if result:
            stats = result[0]
            logger.info(f"Database statistics:")
            logger.info(f"  Total chunks: {stats['total_count']}")
            logger.info(f"  Unique chapters: {stats['unique_chapters']}")
            logger.info(f"  Unique sections: {stats['unique_sections']}")

            if stats['total_count'] > 0:
                logger.info("✓ Metadata sync verification passed")
                return True

        logger.error("✗ No metadata found in database")
        return False

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync chunk metadata to Postgres")
    parser.add_argument(
        "--chunks",
        type=str,
        required=True,
        help="Input chunks JSON file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for syncing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify sync after completion",
    )

    args = parser.parse_args()

    try:
        # Sync metadata
        total_synced = asyncio.run(
            sync_chunk_metadata(
                chunks_file=args.chunks,
                batch_size=args.batch_size,
            )
        )

        # Verify if requested
        if args.verify:
            verification_passed = asyncio.run(verify_sync())

            if not verification_passed:
                logger.error("Metadata sync verification failed")
                sys.exit(1)

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("Metadata Sync Complete")
        logger.info("=" * 50)
        logger.info(f"Total chunks synced: {total_synced}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
