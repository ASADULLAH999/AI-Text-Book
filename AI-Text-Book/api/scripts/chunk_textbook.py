"""
Semantic Chunking Script
Chunks textbook content using LangChain RecursiveCharacterTextSplitter with metadata preservation.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def create_chunk_id(chapter: str, section: str, index: int, content_hash: str = "") -> str:  # Fix: Safe default
    """
    Generate a unique chunk ID.

    Args:
        chapter: Chapter name
        section: Section name
        index: Chunk index within section
        content_hash: Optional content hash for deduplication

    Returns:
        Unique chunk ID
    """
    # Sanitize chapter and section names
    chapter_clean = chapter.replace(" ", "_").replace("/", "-").lower()
    section_clean = section.replace(" ", "_").replace("/", "-").lower()

    chunk_id = f"{chapter_clean}_{section_clean}_{index:04d}"

    if content_hash:
        chunk_id += f"_{content_hash[:8]}"

    return chunk_id


def hash_content(content: str) -> str:
    """Generate hash for content deduplication."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def chunk_document(
    content: str,
    metadata: Dict,
    chunk_size: int = 1024,
    chunk_overlap: float = 0.1,
) -> List[Dict]:
    """
    Chunk a single document using semantic chunking.

    Args:
        content: Document content
        metadata: Document metadata (chapter, section, etc.)
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap percentage (0-1)

    Returns:
        List of chunk dictionaries
    """
    # Initialize text splitter
    overlap_size = int(chunk_size * chunk_overlap)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    # Split text
    text_chunks = text_splitter.split_text(content)

    # Create chunk objects with metadata
    chunks = []
    seen_hashes = set()

    for index, chunk_text in enumerate(text_chunks):
        # Skip very small chunks (< 50 characters)
        if len(chunk_text.strip()) < 50:
            continue

        # Generate content hash
        content_hash = hash_content(chunk_text)

        # Check for duplicates
        if content_hash in seen_hashes:
            print(f"Duplicate chunk detected, skipping: {content_hash[:8]}")
            continue

        seen_hashes.add(content_hash)

        # Find current heading context
        heading = metadata.get("section", "Unknown")
        if metadata.get("headings"):
            # Find nearest preceding heading
            for h in reversed(metadata["headings"]):
                if h["level"] <= 2:  # Use H1 or H2 as heading
                    heading = h["text"]
                    break

        # Create chunk object
        chunk = {
            "chunk_id": create_chunk_id(
                metadata["chapter"],
                metadata["section"],
                index,
                content_hash,
            ),
            "text": chunk_text.strip(),
            "word_count": len(chunk_text.split()),
            "char_count": len(chunk_text),
            "metadata": {
                "chapter": metadata["chapter"],
                "section": metadata["section"],
                "heading": heading,
                "page_number": metadata.get("page_number"),
                "file_path": metadata["file_path"],
                "chunk_index": index,
                "content_hash": content_hash,
            },
        }

        chunks.append(chunk)

    return chunks


def chunk_all_documents(
    metadata_file: str,
    chunk_size: int = 1024,
    chunk_overlap: float = 0.1,
) -> List[Dict]:
    """
    Chunk all documents from metadata file.

    Args:
        metadata_file: Path to file metadata JSON
        chunk_size: Target chunk size
        chunk_overlap: Overlap percentage

    Returns:
        List of all chunks
    """
    # Load metadata
    with open(metadata_file, "r", encoding="utf-8") as f:
        all_metadata = json.load(f)

    print(f"Chunking {len(all_metadata)} documents...")
    print(f"Chunk size: {chunk_size} chars, Overlap: {chunk_overlap * 100}%")

    all_chunks = []
    total_chunks = 0

    for doc_metadata in all_metadata:
        # Read file content
        file_path = doc_metadata["file_path"]

        # Handle relative paths - prepend current directory if path is not absolute
        from pathlib import Path as PathLib
        if not PathLib(file_path).is_absolute():
            file_path = str(PathLib.cwd() / file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        # Remove frontmatter
        import re
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        # Chunk document
        chunks = chunk_document(content, doc_metadata, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
        total_chunks += len(chunks)

        print(f"  {doc_metadata['chapter']}: {len(chunks)} chunks")

    print(f"\nTotal chunks created: {total_chunks}")

    return all_chunks


def deduplicate_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Remove duplicate chunks and merge metadata.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Deduplicated chunks with merged provenance
    """
    unique_chunks = {}

    for chunk in chunks:
        content_hash = chunk["metadata"]["content_hash"]

        if content_hash in unique_chunks:
            # Merge provenance
            existing = unique_chunks[content_hash]
            if "provenance" not in existing["metadata"]:
                existing["metadata"]["provenance"] = [existing["metadata"]["file_path"]]

            existing["metadata"]["provenance"].append(chunk["metadata"]["file_path"])
        else:
            unique_chunks[content_hash] = chunk

    deduplicated = list(unique_chunks.values())
    removed_count = len(chunks) - len(deduplicated)

    print(f"Deduplication removed {removed_count} duplicate chunks")
    print(f"Final unique chunks: {len(deduplicated)}")

    return deduplicated


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Chunk textbook content")
    parser.add_argument(
        "--metadata",
        type=str,
        required=True,
        help="Input file with parsed metadata",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/chunks.json",
        help="Output file for chunks",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=int(os.getenv("RAG_CHUNK_SIZE", "1024")),
        help="Chunk size in characters",
    )
    parser.add_argument(
        "--overlap",
        type=float,
        default=float(os.getenv("RAG_CHUNK_OVERLAP", "0.1")),
        help="Chunk overlap percentage (0-1)",
    )
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        help="Remove duplicate chunks",
    )

    args = parser.parse_args()

    try:
        # Chunk all documents
        chunks = chunk_all_documents(
            args.metadata,
            chunk_size=args.chunk_size,
            chunk_overlap=args.overlap,
        )

        # Deduplicate if requested
        if args.deduplicate:
            chunks = deduplicate_chunks(chunks)

        # Save chunks
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        print(f"\nSaved {len(chunks)} chunks to: {output_path}")

        # Print statistics
        total_words = sum(c["word_count"] for c in chunks)
        avg_words = total_words / len(chunks) if chunks else 0

        print(f"\nChunk Statistics:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Total words: {total_words:,}")
        print(f"  Average words per chunk: {avg_words:.1f}")

        # Chapter distribution
        chapters = {}
        for c in chunks:
            chapter = c["metadata"]["chapter"]
            chapters[chapter] = chapters.get(chapter, 0) + 1

        print(f"\nChapter distribution:")
        for chapter, count in sorted(chapters.items()):
            print(f"  {chapter}: {count} chunks")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
