"""
Citation Service
Generates and validates citations from retrieved chunks.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CitationService:
    """Service for generating and validating citations.

    T085 [US4] — Citation generation is tone-agnostic by design.
    Tone affects language style only; chunk IDs, source metadata, confidence
    scores, and citation structure are derived solely from retrieved chunks and
    are never modified by tone selection.
    """

    def __init__(self):
        """Initialize the citation service."""
        logger.info("Initialized CitationService")

    def generate_citations(
        self,
        chunks: List[Dict[str, Any]],
        response_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate citations from retrieved chunks.

        Args:
            chunks: Retrieved chunks with metadata
            response_text: Optional response text to match citations to

        Returns:
            List of citation objects
        """
        logger.debug(f"Generating citations from {len(chunks)} chunks")

        citations = []
        for idx, chunk in enumerate(chunks):
            citation = self._create_citation(chunk, idx + 1)
            citations.append(citation)

        logger.info(f"Generated {len(citations)} citations")
        return citations

    def _create_citation(
        self,
        chunk: Dict[str, Any],
        citation_number: int,
    ) -> Dict[str, Any]:
        """
        Create a citation object from a chunk.

        Args:
            chunk: Chunk data with metadata
            citation_number: Citation number/index

        Returns:
            Citation object
        """
        metadata = chunk.get("metadata", {})

        citation = {
            "id": f"cite-{citation_number}",
            "number": citation_number,
            "chunk_id": chunk.get("chunk_id"),
            "text": chunk.get("text", ""),
            "score": chunk.get("rerank_score") or chunk.get("score", 0.0),
            "source": {
                "chapter": metadata.get("chapter", "Unknown Chapter"),
                "section": metadata.get("section", "Unknown Section"),
                "heading": metadata.get("heading"),
                "page_number": metadata.get("page_number"),
            },
            "preview": self._create_preview(chunk.get("text", "")),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return citation

    def _create_preview(self, text: str, max_length: int = 150) -> str:
        """
        Create a preview snippet from text.

        Args:
            text: Full text
            max_length: Maximum preview length

        Returns:
            Preview text with ellipsis if truncated
        """
        if len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + "..."

    def validate_citation(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a citation object.

        Args:
            citation: Citation to validate

        Returns:
            Validation result with errors if any
        """
        errors = []

        # Required fields
        required_fields = ["id", "number", "chunk_id", "text", "source"]
        for field in required_fields:
            if field not in citation:
                errors.append(f"Missing required field: {field}")

        # Source validation
        if "source" in citation:
            source = citation["source"]
            if not source.get("chapter"):
                errors.append("Citation missing chapter information")
            if not source.get("section"):
                errors.append("Citation missing section information")

        # Text validation
        if "text" in citation and not citation["text"].strip():
            errors.append("Citation text is empty")

        is_valid = len(errors) == 0

        result = {
            "is_valid": is_valid,
            "errors": errors,
        }

        if not is_valid:
            logger.warning(f"Invalid citation: {errors}")

        return result

    def format_citation_text(
        self,
        citation: Dict[str, Any],
        format_style: str = "apa",
    ) -> str:
        """
        Format citation as text string.

        Args:
            citation: Citation object
            format_style: Citation style (apa, mla, chicago)

        Returns:
            Formatted citation string
        """
        source = citation.get("source", {})
        chapter = source.get("chapter", "Unknown")
        section = source.get("section", "Unknown")
        page = source.get("page_number")

        if format_style == "apa":
            # APA style: Chapter. Section. (Page X)
            parts = [chapter, section]
            if page:
                parts.append(f"(Page {page})")
            return ". ".join(parts)

        elif format_style == "inline":
            # Inline style: [Chapter - Section]
            return f"[{chapter} - {section}]"

        else:
            # Default: Simple format
            parts = [chapter, section]
            if page:
                parts.append(f"p. {page}")
            return " | ".join(parts)

    def deduplicate_citations(
        self,
        citations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate citations based on chunk_id.

        Args:
            citations: List of citations

        Returns:
            Deduplicated citation list
        """
        seen_chunk_ids = set()
        unique_citations = []

        for citation in citations:
            chunk_id = citation.get("chunk_id")
            if chunk_id and chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                unique_citations.append(citation)

        if len(unique_citations) < len(citations):
            logger.info(
                f"Deduplicated citations: {len(citations)} → {len(unique_citations)}"
            )

        return unique_citations

    def validate_tone_isolation(
        self,
        citations_tone_a: List[Dict[str, Any]],
        citations_tone_b: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        T085 [US4] — Assert that two citation lists (generated from the same chunks
        under different tones) are structurally identical.

        Checks chunk_id, source metadata, and score for each citation pair.
        Does NOT compare timestamps, which are allowed to differ.

        Args:
            citations_tone_a: Citations generated with tone A.
            citations_tone_b: Citations generated with tone B.

        Returns:
            dict with keys:
                "is_isolated" (bool): True if citations are tone-agnostic.
                "mismatches" (list[str]): Descriptions of any differences found.
        """
        mismatches: List[str] = []

        if len(citations_tone_a) != len(citations_tone_b):
            mismatches.append(
                f"Citation count differs: {len(citations_tone_a)} vs {len(citations_tone_b)}"
            )
            return {"is_isolated": False, "mismatches": mismatches}

        _STRUCTURAL_KEYS = ("chunk_id", "score", "source")

        for idx, (ca, cb) in enumerate(zip(citations_tone_a, citations_tone_b)):
            for key in _STRUCTURAL_KEYS:
                if ca.get(key) != cb.get(key):
                    mismatches.append(
                        f"Citation [{idx}] '{key}' differs: {ca.get(key)!r} vs {cb.get(key)!r}"
                    )

        if mismatches:
            logger.warning(f"Tone isolation violation detected: {mismatches}")

        return {"is_isolated": len(mismatches) == 0, "mismatches": mismatches}


# Singleton instance
_citation_service = None


def get_citation_service() -> CitationService:
    """Get or create the singleton CitationService instance."""
    global _citation_service
    if _citation_service is None:
        _citation_service = CitationService()
    return _citation_service
