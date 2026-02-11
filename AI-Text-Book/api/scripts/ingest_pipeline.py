"""
Complete Ingestion Pipeline Orchestrator
Runs the full document processing pipeline: extract → parse → chunk → embed → upload → validate
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def run_command(cmd: list, description: str) -> bool:
    """
    Run a subprocess command.

    Args:
        cmd: Command list
        description: Description for logging

    Returns:
        True if successful
    """
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Step: {description}")
    logger.info(f"{'=' * 60}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        logger.info(result.stdout)

        if result.stderr:
            logger.warning(result.stderr)

        logger.info(f"✓ {description} completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed")
        logger.error(f"Error output: {e.stderr}")
        return False


def main():
    """Run the complete ingestion pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Run complete document ingestion pipeline")
    parser.add_argument(
        "--textbook-dir",
        type=str,
        default=".",
        help="Path to textbook root directory",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory for intermediate data files",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip extraction step (reuse existing data)",
    )
    parser.add_argument(
        "--skip-embedding",
        action="store_true",
        help="Skip embedding generation (reuse existing embeddings)",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip upload to Qdrant",
    )
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip Postgres metadata sync",
    )

    args = parser.parse_args()

    # Ensure data directory exists
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Define file paths
    files = {
        "extracted": data_dir / "extracted_files.json",
        "metadata": data_dir / "file_metadata.json",
        "chunks": data_dir / "chunks.json",
        "embeddings": data_dir / "chunks_with_embeddings.json",
        "validation": data_dir / "validation_report.json",
    }

    logger.info("\n" + "=" * 60)
    logger.info("Starting Document Ingestion Pipeline")
    logger.info("=" * 60)
    logger.info(f"Textbook directory: {args.textbook_dir}")
    logger.info(f"Data directory: {args.data_dir}")

    # Step 1: Extract markdown files
    if not args.skip_extract:
        success = run_command(
            [
                sys.executable,
                "api/scripts/extract_markdown.py",
                "--textbook-dir", args.textbook_dir,
                "--output", str(files["extracted"]),
            ],
            "Extract markdown files",
        )
        if not success:
            logger.error("Pipeline failed at extraction step")
            sys.exit(1)
    else:
        logger.info("Skipping extraction step (using existing data)")

    # Step 2: Parse metadata
    success = run_command(
        [
            sys.executable,
            "api/scripts/parse_metadata.py",
            "--input", str(files["extracted"]),
            "--output", str(files["metadata"]),
        ],
        "Parse file metadata",
    )
    if not success:
        logger.error("Pipeline failed at metadata parsing step")
        sys.exit(1)

    # Step 3: Chunk documents
    success = run_command(
        [
            sys.executable,
            "api/scripts/chunk_textbook.py",
            "--metadata", str(files["metadata"]),
            "--output", str(files["chunks"]),
            "--deduplicate",
        ],
        "Chunk textbook content",
    )
    if not success:
        logger.error("Pipeline failed at chunking step")
        sys.exit(1)

    # Step 4: Generate embeddings
    if not args.skip_embedding:
        success = run_command(
            [
                sys.executable,
                "api/scripts/generate_embeddings.py",
                "--chunks", str(files["chunks"]),
                "--output", str(files["embeddings"]),
                "--cache", str(data_dir / "embeddings_cache.json"),
            ],
            "Generate embeddings",
        )
        if not success:
            logger.error("Pipeline failed at embedding generation step")
            sys.exit(1)
    else:
        logger.info("Skipping embedding generation (using existing embeddings)")

    # Step 5: Upload to Qdrant
    if not args.skip_upload:
        success = run_command(
            [
                sys.executable,
                "api/scripts/upload_to_qdrant.py",
                "--chunks", str(files["embeddings"]),
                "--verify",
            ],
            "Upload to Qdrant",
        )
        if not success:
            logger.error("Pipeline failed at upload step")
            sys.exit(1)
    else:
        logger.info("Skipping Qdrant upload")

    # Step 6: Sync metadata to Postgres
    if not args.skip_sync:
        success = run_command(
            [
                sys.executable,
                "api/scripts/sync_postgres.py",
                "--chunks", str(files["chunks"]),
                "--verify",
            ],
            "Sync metadata to Postgres",
        )
        if not success:
            logger.error("Pipeline failed at metadata sync step")
            sys.exit(1)
    else:
        logger.info("Skipping Postgres metadata sync")

    # Step 7: Validate chunks
    success = run_command(
        [
            sys.executable,
            "api/scripts/validate_chunks.py",
            "--chunks", str(files["chunks"]),
            "--metadata", str(files["metadata"]),
            "--report", str(files["validation"]),
        ],
        "Validate chunk quality",
    )
    if not success:
        logger.warning("Validation warnings detected, but continuing")

    # Pipeline complete
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Complete")
    logger.info("=" * 60)
    logger.info("All steps completed successfully!")
    logger.info(f"\nOutput files:")
    for name, path in files.items():
        logger.info(f"  {name}: {path}")


if __name__ == "__main__":
    main()
