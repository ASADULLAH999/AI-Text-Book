"""
Generate Embeddings Script
Batch processes chunks and generates embeddings using OpenAI API.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional  # Fix: Add Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables from api/.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.embedding_service import get_embedding_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def generate_embeddings_for_chunks(
    chunks_file: str,
    output_file: str,
    batch_size: int = 100,
    cache_file: Optional[str] = None,  # Fix: Optional type
) -> List[Dict]:
    """
    Generate embeddings for all chunks.

    Args:
        chunks_file: Path to chunks JSON file
        output_file: Path to save chunks with embeddings
        batch_size: Batch size for processing
        cache_file: Optional path to cache file for resuming

    Returns:
        List of chunks with embeddings
    """
    # Load chunks
    logger.info(f"Loading chunks from: {chunks_file}")
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks")

    # Load cache if exists
    processed_chunks = {}
    if cache_file and Path(cache_file).exists():
        logger.info(f"Loading cache from: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
            for chunk in cached_data:
                processed_chunks[chunk["chunk_id"]] = chunk
        logger.info(f"Loaded {len(processed_chunks)} cached chunks")

    # Get embedding service
    embedding_service = get_embedding_service()

    # Process chunks
    chunks_with_embeddings = []
    total_processed = 0

    for i, chunk in enumerate(chunks):
        chunk_id = chunk["chunk_id"]

        # Check if already processed
        if chunk_id in processed_chunks:
            chunks_with_embeddings.append(processed_chunks[chunk_id])
            total_processed += 1
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i + 1}/{len(chunks)} (using cache)")
            continue

        # Generate embedding
        try:
            text = chunk["text"]
            embedding = await embedding_service.embed_text(text)

            # Add embedding to chunk
            chunk_with_embedding = {
                **chunk,
                "embedding": embedding,
            }

            chunks_with_embeddings.append(chunk_with_embedding)
            processed_chunks[chunk_id] = chunk_with_embedding
            total_processed += 1

            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(chunks)} chunks processed")

            # Save cache periodically
            if cache_file and (i + 1) % 100 == 0:
                logger.info(f"Saving cache checkpoint...")
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(chunks_with_embeddings, f, indent=2)

        except Exception as e:
            logger.error(f"Error processing chunk {chunk_id}: {e}")
            # Save partial results
            if cache_file:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(chunks_with_embeddings, f, indent=2)
            raise

    # Save final results
    logger.info(f"Saving {len(chunks_with_embeddings)} chunks with embeddings to: {output_file}")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks_with_embeddings, f, indent=2)

    # Save cache
    if cache_file:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(chunks_with_embeddings, f, indent=2)
        logger.info(f"Saved cache to: {cache_file}")

    logger.info(f"Successfully generated embeddings for {total_processed} chunks")

    # Statistics
    cache_stats = embedding_service.get_cache_size()
    logger.info(f"Embedding cache size: {cache_stats} entries")

    return chunks_with_embeddings


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for chunks")
    parser.add_argument(
        "--chunks",
        type=str,
        required=True,
        help="Input chunks JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/chunks_with_embeddings.json",
        help="Output file for chunks with embeddings",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing",
    )
    parser.add_argument(
        "--cache",
        type=str,
        default="../data/embeddings_cache.json",
        help="Cache file for resuming interrupted runs",
    )

    args = parser.parse_args()

    try:
        # Run async function
        chunks_with_embeddings = asyncio.run(
            generate_embeddings_for_chunks(
                chunks_file=args.chunks,
                output_file=args.output,
                batch_size=args.batch_size,
                cache_file=args.cache,
            )
        )

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("Embedding Generation Complete")
        logger.info("=" * 50)
        logger.info(f"Total chunks processed: {len(chunks_with_embeddings)}")
        logger.info(f"Output file: {args.output}")

    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user. Progress saved to cache.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
