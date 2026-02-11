"""
Parse Metadata from Markdown Files
Extracts chapter, section, and heading hierarchy from frontmatter and markdown headings.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def parse_frontmatter(content: str) -> Dict[str, any]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Dictionary of frontmatter metadata
    """
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        try:
            frontmatter_text = match.group(1)
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter or {}
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse frontmatter: {e}")
            return {}

    return {}


def extract_heading_hierarchy(content: str) -> List[Dict[str, any]]:
    """
    Extract heading hierarchy from markdown content.

    Args:
        content: Markdown file content

    Returns:
        List of heading dictionaries with level, text, and line number
    """
    headings = []

    # Remove frontmatter
    content_without_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Extract headings (# to ######)
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content_without_frontmatter.split('\n')

    for line_num, line in enumerate(lines, start=1):
        match = re.match(heading_pattern, line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()

            headings.append({
                "level": level,
                "text": text,
                "line": line_num,
            })

    return headings


def infer_chapter_section(file_path: str, frontmatter: Dict, headings: List[Dict]) -> Dict[str, str]:
    """
    Infer chapter and section from file path, frontmatter, and headings.

    Args:
        file_path: Relative file path
        frontmatter: Parsed frontmatter
        headings: List of heading dictionaries

    Returns:
        Dictionary with chapter, section, and page_number
    """
    metadata = {
        "chapter": "Unknown",
        "section": "Unknown",
        "page_number": None,
    }

    # Try frontmatter first
    if "chapter" in frontmatter:
        metadata["chapter"] = frontmatter["chapter"]
    if "section" in frontmatter:
        metadata["section"] = frontmatter["section"]
    if "page" in frontmatter:
        metadata["page_number"] = frontmatter["page"]

    # Try to infer from file path
    path_parts = Path(file_path).parts
    if len(path_parts) >= 2:
        # Assume structure like: module-1/chapter-1-intro.md
        if metadata["chapter"] == "Unknown":
            # Extract chapter from filename or directory
            for part in path_parts:
                if "chapter" in part.lower() or "module" in part.lower():
                    metadata["chapter"] = part.replace("-", " ").title()
                    break

    # Try to infer from first heading
    if headings and metadata["chapter"] == "Unknown":
        first_heading = headings[0]
        if first_heading["level"] == 1:
            metadata["chapter"] = first_heading["text"]

    # Section from second heading or first H2
    if headings and metadata["section"] == "Unknown":
        for heading in headings:
            if heading["level"] == 2:
                metadata["section"] = heading["text"]
                break

    return metadata


def parse_file_metadata(file_path: str, content: str) -> Dict[str, any]:
    """
    Parse complete metadata from a markdown file.

    Args:
        file_path: File path (relative)
        content: File content

    Returns:
        Complete metadata dictionary
    """
    frontmatter = parse_frontmatter(content)
    headings = extract_heading_hierarchy(content)
    chapter_section = infer_chapter_section(file_path, frontmatter, headings)

    metadata = {
        "file_path": file_path,
        "frontmatter": frontmatter,
        "headings": headings,
        "chapter": chapter_section["chapter"],
        "section": chapter_section["section"],
        "page_number": chapter_section["page_number"],
        "heading_count": len(headings),
        "word_count": len(content.split()),
    }

    return metadata


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse metadata from markdown files")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input JSON file with extracted files list",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/file_metadata.json",
        help="Output file for parsed metadata",
    )

    args = parser.parse_args()

    try:
        # Load extracted files list
        with open(args.input, "r", encoding="utf-8") as f:
            files = json.load(f)

        print(f"Parsing metadata for {len(files)} files...")

        # Parse each file
        all_metadata = []
        for file_info in files:
            file_path = file_info["file_path"]
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = parse_file_metadata(file_info["relative_path"], content)
            all_metadata.append(metadata)

        # Save metadata
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_metadata, f, indent=2)

        print(f"Saved metadata to: {output_path}")

        # Print summary
        print(f"\nMetadata Summary:")
        print(f"  Total files: {len(all_metadata)}")

        # Chapter distribution
        chapters = {}
        for m in all_metadata:
            chapter = m["chapter"]
            chapters[chapter] = chapters.get(chapter, 0) + 1

        print(f"\nChapter distribution:")
        for chapter, count in sorted(chapters.items()):
            print(f"  {chapter}: {count} files")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
