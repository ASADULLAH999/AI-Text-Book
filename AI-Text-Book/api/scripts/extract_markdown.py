"""
Extract Markdown Files from Textbook
Extracts all markdown files from TextBook/docs/ directory with metadata preservation.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def extract_markdown_files(textbook_dir: str, output_file: str = None) -> List[Dict[str, any]]:
    """
    Extract all markdown files from the textbook directory.

    Args:
        textbook_dir: Path to textbook root directory
        output_file: Optional path to save extracted files list

    Returns:
        List of file metadata dictionaries
    """
    textbook_path = Path(textbook_dir)
    docs_path = textbook_path / "docs"

    if not docs_path.exists():
        # Try alternative path (TextBook/docs or docs/)
        if (textbook_path / "TextBook" / "docs").exists():
            docs_path = textbook_path / "TextBook" / "docs"
        elif (textbook_path.parent / "TextBook" / "docs").exists():
            docs_path = textbook_path.parent / "TextBook" / "docs"
        else:
            raise ValueError(f"Cannot find docs directory in {textbook_dir}")

    print(f"Extracting markdown files from: {docs_path}")

    markdown_files = []
    for file_path in docs_path.rglob("*.md"):
        # Skip non-content files
        if any(skip in str(file_path) for skip in ["node_modules", ".git", "README"]):
            continue

        relative_path = file_path.relative_to(docs_path)
        file_metadata = {
            "file_path": str(file_path),
            "relative_path": str(relative_path),
            "file_name": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "directory": str(relative_path.parent),
        }

        markdown_files.append(file_metadata)

    print(f"Found {len(markdown_files)} markdown files")

    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(markdown_files, f, indent=2)

        print(f"Saved file list to: {output_path}")

    return markdown_files


def read_markdown_content(file_path: str) -> str:
    """Read markdown file content."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract markdown files from textbook")
    parser.add_argument(
        "--textbook-dir",
        type=str,
        default=".",
        help="Path to textbook root directory",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/extracted_files.json",
        help="Output file for extracted files list",
    )

    args = parser.parse_args()

    try:
        files = extract_markdown_files(args.textbook_dir, args.output)

        # Print summary
        total_size = sum(f["size_bytes"] for f in files)
        print(f"\nExtraction Summary:")
        print(f"  Total files: {len(files)}")
        print(f"  Total size: {total_size / 1024:.2f} KB")

        # Print directory distribution
        directories = {}
        for f in files:
            dir_name = f["directory"]
            directories[dir_name] = directories.get(dir_name, 0) + 1

        print(f"\nDirectory distribution:")
        for dir_name, count in sorted(directories.items()):
            print(f"  {dir_name}: {count} files")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
