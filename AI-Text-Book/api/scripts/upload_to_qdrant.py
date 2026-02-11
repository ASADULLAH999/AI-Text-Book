"""
Upload to Qdrant Script
Batch uploads chunks with embeddings to Qdrant vector database.
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

from db.qdrant_client import qdrant_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def upload_chunks_to_qdrant(
    chunks_file: str,
    batch_size: int = 100,
) -> int:
    """
    Upload chunks with embeddings to Qdrant.

    Args:
        chunks_file: Path to chunks with embeddings JSON file
        batch_size: Number of chunks to upload per batch

    Returns:
        Number of chunks uploaded
    """
    # Load chunks with embeddings
    logger.info(f"Loading chunks from: {chunks_file}")
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks with embeddings")

    # Verify embeddings exist
    chunks_with_embeddings = [c for c in chunks if "embedding" in c]
    if len(chunks_with_embeddings) < len(chunks):
        logger.warning(
            f"Only {len(chunks_with_embeddings)}/{len(chunks)} chunks have embeddings"
        )

    # Ensure collection exists
    logger.info("Ensuring Qdrant collection exists...")
    await qdrant_client.ensure_collection_exists()

    # Upload in batches
    total_uploaded = 0
    batch_count = (len(chunks_with_embeddings) + batch_size - 1) // batch_size

    for i in range(0, len(chunks_with_embeddings), batch_size):
        batch = chunks_with_embeddings[i:i + batch_size]
        batch_num = i // batch_size + 1

        logger.info(f"Uploading batch {batch_num}/{batch_count} ({len(batch)} chunks)...")

        try:
            # Upsert batch to Qdrant
            uploaded_count = await qdrant_client.upsert_chunks(batch)
            total_uploaded += uploaded_count

            logger.info(f"Batch {batch_num} uploaded successfully ({uploaded_count} chunks)")

        except Exception as e:
            logger.error(f"Error uploading batch {batch_num}: {e}")
            raise

    logger.info(f"Successfully uploaded {total_uploaded} chunks to Qdrant")
    return total_uploaded


async def verify_upload(
    sample_chunk_ids: List[str] = None,
    sample_size: int = 5,
) -> bool:
    """
    Verify that chunks were uploaded correctly by sampling.

    Args:
        sample_chunk_ids: Specific chunk IDs to verify
        sample_size: Number of random chunks to verify

    Returns:
        True if verification passed
    """
    logger.info("Verifying upload...")

    if sample_chunk_ids:
        for chunk_id in sample_chunk_ids:
            try:
                chunk = await qdrant_client.get_chunk_by_id(chunk_id)
                if chunk:
                    logger.info(f"✓ Verified chunk: {chunk_id}")
                else:
                    logger.error(f"✗ Chunk not found: {chunk_id}")
                    return False
            except Exception as e:
                logger.error(f"✗ Error verifying chunk {chunk_id}: {e}")
                return False

    logger.info("Upload verification passed")
    return True


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Upload chunks to Qdrant")
    parser.add_argument(
        "--chunks",
        type=str,
        required=True,
        help="Input chunks with embeddings JSON file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for uploading",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify upload after completion",
    )
    parser.add_argument(
        "--verify-chunk-ids",
        type=str,
        nargs="+",
        help="Specific chunk IDs to verify",
    )

    args = parser.parse_args()

    try:
        # Upload chunks
        total_uploaded = asyncio.run(
            upload_chunks_to_qdrant(
                chunks_file=args.chunks,
                batch_size=args.batch_size,
            )
        )

        # Verify if requested
        if args.verify:
            verification_passed = asyncio.run(
                verify_upload(
                    sample_chunk_ids=args.verify_chunk_ids,
                )
            )

            if not verification_passed:
                logger.error("Upload verification failed")
                sys.exit(1)

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("Upload Complete")
        logger.info("=" * 50)
        logger.info(f"Total chunks uploaded: {total_uploaded}")
        logger.info(f"Qdrant collection: {qdrant_client.get_collection_name()}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
