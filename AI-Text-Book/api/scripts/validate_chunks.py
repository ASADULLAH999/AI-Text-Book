"""
Validate Chunks Script
Verifies chunk quality: coverage, overlap correctness, metadata completeness.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def validate_chunk_coverage(chunks: List[Dict], metadata: List[Dict]) -> bool:
    """
    Verify that all chapters are covered by chunks.

    Args:
        chunks: List of chunk dictionaries
        metadata: List of file metadata dictionaries

    Returns:
        True if validation passed
    """
    logger.info("Validating chunk coverage...")

    # Get unique chapters from metadata
    expected_chapters = set(m["chapter"] for m in metadata)

    # Get unique chapters from chunks
    actual_chapters = set(c["metadata"]["chapter"] for c in chunks)

    # Check coverage
    missing_chapters = expected_chapters - actual_chapters
    extra_chapters = actual_chapters - expected_chapters

    if missing_chapters:
        logger.warning(f"Missing chapters in chunks: {missing_chapters}")
        return False

    if extra_chapters:
        logger.warning(f"Extra chapters in chunks: {extra_chapters}")

    logger.info(f"✓ All {len(expected_chapters)} chapters covered")
    return True


def validate_overlap_correctness(chunks: List[Dict]) -> bool:
    """
    Verify that chunk overlaps are reasonable.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        True if validation passed
    """
    logger.info("Validating chunk overlaps...")

    # Group chunks by chapter and section
    grouped_chunks = defaultdict(list)
    for chunk in chunks:
        key = (chunk["metadata"]["chapter"], chunk["metadata"]["section"])
        grouped_chunks[key].append(chunk)

    issues_found = 0

    for (chapter, section), group in grouped_chunks.items():
        if len(group) < 2:
            continue  # No overlap to check

        # Sort by chunk index
        sorted_chunks = sorted(group, key=lambda c: c["metadata"]["chunk_index"])

        # Check overlaps between consecutive chunks
        for i in range(len(sorted_chunks) - 1):
            chunk1 = sorted_chunks[i]
            chunk2 = sorted_chunks[i + 1]

            text1 = chunk1["text"]
            text2 = chunk2["text"]

            # Calculate overlap (simplified check)
            overlap_length = len(set(text1.split()) & set(text2.split()))
            overlap_ratio = overlap_length / max(len(text1.split()), 1)

            # Expect 5-15% overlap
            if overlap_ratio < 0.05 or overlap_ratio > 0.20:
                logger.warning(
                    f"Unusual overlap ratio {overlap_ratio:.2%} between chunks "
                    f"in {chapter}/{section}"
                )
                issues_found += 1

    if issues_found > 0:
        logger.warning(f"Found {issues_found} potential overlap issues")
        return False

    logger.info("✓ Chunk overlaps are reasonable")
    return True


def validate_metadata_completeness(chunks: List[Dict]) -> bool:
    """
    Verify that all chunks have complete metadata.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        True if validation passed
    """
    logger.info("Validating metadata completeness...")

    required_fields = [
        "chunk_id",
        "text",
        "word_count",
        "metadata",
    ]

    required_metadata_fields = [
        "chapter",
        "section",
        "file_path",
        "chunk_index",
    ]

    incomplete_chunks = []

    for chunk in chunks:
        # Check required fields
        missing_fields = [f for f in required_fields if f not in chunk]
        if missing_fields:
            incomplete_chunks.append({
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "missing_fields": missing_fields,
            })
            continue

        # Check metadata fields
        metadata = chunk.get("metadata", {})
        missing_metadata = [f for f in required_metadata_fields if f not in metadata]
        if missing_metadata:
            incomplete_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "missing_metadata": missing_metadata,
            })

    if incomplete_chunks:
        logger.error(f"Found {len(incomplete_chunks)} chunks with incomplete metadata")
        for chunk_info in incomplete_chunks[:5]:  # Show first 5
            logger.error(f"  {chunk_info}")
        return False

    logger.info("✓ All chunks have complete metadata")
    return True


def validate_chunk_sizes(chunks: List[Dict], min_words: int = 10, max_words: int = 500) -> bool:
    """
    Verify that chunk sizes are reasonable.

    Args:
        chunks: List of chunk dictionaries
        min_words: Minimum word count
        max_words: Maximum word count

    Returns:
        True if validation passed
    """
    logger.info(f"Validating chunk sizes (min: {min_words}, max: {max_words} words)...")

    too_small = []
    too_large = []

    for chunk in chunks:
        word_count = chunk["word_count"]

        if word_count < min_words:
            too_small.append(chunk["chunk_id"])
        elif word_count > max_words:
            too_large.append(chunk["chunk_id"])

    if too_small:
        logger.warning(f"Found {len(too_small)} chunks below minimum size")

    if too_large:
        logger.warning(f"Found {len(too_large)} chunks above maximum size")

    # Calculate statistics
    word_counts = [c["word_count"] for c in chunks]
    avg_words = sum(word_counts) / len(word_counts)
    min_words_found = min(word_counts)
    max_words_found = max(word_counts)

    logger.info(f"Chunk size statistics:")
    logger.info(f"  Average: {avg_words:.1f} words")
    logger.info(f"  Minimum: {min_words_found} words")
    logger.info(f"  Maximum: {max_words_found} words")

    return len(too_small) < len(chunks) * 0.05  # Allow 5% undersized chunks


def generate_validation_report(
    chunks: List[Dict],
    metadata: List[Dict],
    output_file: str = None,
) -> Dict:
    """
    Generate comprehensive validation report.

    Args:
        chunks: List of chunk dictionaries
        metadata: List of file metadata dictionaries
        output_file: Optional path to save report

    Returns:
        Validation report dictionary
    """
    logger.info("Generating validation report...")

    # Run all validations
    results = {
        "total_chunks": len(chunks),
        "coverage_valid": validate_chunk_coverage(chunks, metadata),
        "overlap_valid": validate_overlap_correctness(chunks),
        "metadata_complete": validate_metadata_completeness(chunks),
        "sizes_reasonable": validate_chunk_sizes(chunks),
    }

    # Calculate overall status
    results["overall_valid"] = all([
        results["coverage_valid"],
        results["overlap_valid"],
        results["metadata_complete"],
        results["sizes_reasonable"],
    ])

    # Save report if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved validation report to: {output_path}")

    return results


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate chunk quality")
    parser.add_argument(
        "--chunks",
        type=str,
        required=True,
        help="Input chunks JSON file",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        help="Input file metadata JSON file (for coverage check)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="data/validation_report.json",
        help="Output validation report file",
    )

    args = parser.parse_args()

    try:
        # Load chunks
        with open(args.chunks, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        logger.info(f"Loaded {len(chunks)} chunks")

        # Load metadata if provided
        metadata = []
        if args.metadata:
            with open(args.metadata, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            logger.info(f"Loaded {len(metadata)} metadata records")

        # Generate validation report
        report = generate_validation_report(chunks, metadata, args.report)

        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("Validation Summary")
        logger.info("=" * 50)
        logger.info(f"Total chunks: {report['total_chunks']}")
        logger.info(f"Coverage valid: {'✓' if report['coverage_valid'] else '✗'}")
        logger.info(f"Overlap valid: {'✓' if report['overlap_valid'] else '✗'}")
        logger.info(f"Metadata complete: {'✓' if report['metadata_complete'] else '✗'}")
        logger.info(f"Sizes reasonable: {'✓' if report['sizes_reasonable'] else '✗'}")
        logger.info(f"\nOverall: {'✓ PASSED' if report['overall_valid'] else '✗ FAILED'}")

        if not report['overall_valid']:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
