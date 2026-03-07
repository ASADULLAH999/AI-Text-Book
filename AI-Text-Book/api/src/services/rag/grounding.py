"""
RAG Grounding Service
Validates that LLM responses are grounded in retrieved context and detects hallucinations.
"""

from typing import List, Dict, Any, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class GroundingService:
    """Service for validating response grounding and detecting hallucinations."""

    def __init__(
        self,
        min_overlap_ratio: float = 0.3,
        min_citation_coverage: float = 0.7,
    ):
        """
        Initialize the grounding service.

        Args:
            min_overlap_ratio: Minimum content overlap required
            min_citation_coverage: Minimum citation coverage required
        """
        self.min_overlap_ratio = min_overlap_ratio
        self.min_citation_coverage = min_citation_coverage
        logger.info(
            f"Initialized GroundingService "
            f"(overlap={min_overlap_ratio}, coverage={min_citation_coverage})"
        )

    def validate_grounding(
        self,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate that a response is grounded in retrieved chunks.

        Args:
            response: LLM-generated response
            retrieved_chunks: Retrieved context chunks

        Returns:
            Validation result with grounding metrics
        """
        logger.debug("Validating response grounding")

        # Extract sentences from response
        response_sentences = self._extract_sentences(response)

        # Extract all context text
        context_text = " ".join([
            chunk.get("text", "") for chunk in retrieved_chunks
        ]).lower()

        # Check sentence grounding
        grounded_sentences = 0
        ungrounded_sentences = []

        for sentence in response_sentences:
            if self._is_grounded(sentence, context_text):
                grounded_sentences += 1
            else:
                ungrounded_sentences.append(sentence)

        # Calculate grounding ratio
        total_sentences = len(response_sentences)
        grounding_ratio = (
            grounded_sentences / total_sentences if total_sentences > 0 else 0.0
        )

        is_grounded = grounding_ratio >= self.min_overlap_ratio

        result = {
            "is_grounded": is_grounded,
            "grounding_ratio": grounding_ratio,
            "grounded_sentences": grounded_sentences,
            "total_sentences": total_sentences,
            "ungrounded_sentences": ungrounded_sentences[:3],  # Sample for debugging
        }

        logger.info(
            f"Grounding validation: {grounding_ratio:.2%} "
            f"({grounded_sentences}/{total_sentences} sentences grounded)"
        )

        return result

    def detect_hallucination(
        self,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Detect potential hallucinations in the response.

        Hallucination indicators:
        1. Claims not found in retrieved chunks
        2. Specific facts/numbers without citations
        3. Low citation coverage

        Args:
            response: LLM-generated response
            retrieved_chunks: Retrieved context chunks
            citations: Extracted citations

        Returns:
            Hallucination detection result
        """
        logger.debug("Detecting potential hallucinations")

        # Check grounding first
        grounding_result = self.validate_grounding(response, retrieved_chunks)

        # Check citation coverage
        citation_coverage = self._calculate_citation_coverage(response, citations)

        # Detect specific fact claims without citations
        uncited_facts = self._detect_uncited_facts(response, citations)

        # Overall hallucination risk
        hallucination_risk = self._calculate_hallucination_risk(
            grounding_result["grounding_ratio"],
            citation_coverage,
            len(uncited_facts),
        )

        result = {
            "hallucination_risk": hallucination_risk,
            "grounding_ratio": grounding_result["grounding_ratio"],
            "citation_coverage": citation_coverage,
            "uncited_facts": uncited_facts[:5],  # Sample
            "is_safe": hallucination_risk < 0.3,  # Low risk threshold
        }

        logger.info(
            f"Hallucination detection: risk={hallucination_risk:.2%}, "
            f"coverage={citation_coverage:.2%}"
        )

        return result

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Simple sentence splitting (could be improved with NLTK)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _is_grounded(self, sentence: str, context: str) -> bool:
        """Check if a sentence is grounded in context."""
        sentence_lower = sentence.lower()

        # Extract significant words (> 3 chars, not common stop words)
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'with', 'this', 'that'}
        words = [
            w for w in sentence_lower.split()
            if len(w) > 3 and w not in stop_words
        ]

        if not words:
            return True  # Empty/trivial sentence

        # Check word overlap
        found_words = sum(1 for word in words if word in context)
        overlap_ratio = found_words / len(words)

        return overlap_ratio >= 0.5  # At least 50% word overlap

    def _calculate_citation_coverage(
        self,
        response: str,
        citations: List[Dict[str, Any]],
    ) -> float:
        """Calculate what percentage of response is covered by citations."""
        if not citations:
            return 0.0

        # Simple heuristic: ratio of sentences with citations
        sentences = self._extract_sentences(response)
        if not sentences:
            return 0.0

        # Count cited sentences (sentences near citation markers)
        cited_count = 0
        for citation in citations:
            # Assume citation has 'text' field indicating cited content
            cited_text = citation.get("text", "")
            if cited_text and cited_text in response:
                cited_count += 1

        # Estimate coverage
        coverage = min(cited_count / len(sentences), 1.0)
        return coverage

    def _detect_uncited_facts(
        self,
        response: str,
        citations: List[Dict[str, Any]],
    ) -> List[str]:
        """Detect specific factual claims without citations."""
        uncited_facts = []

        # Patterns that indicate specific facts
        fact_patterns = [
            r'\d{4}',  # Years
            r'\d+%',   # Percentages
            r'\d+\.\d+',  # Decimal numbers
            r'according to',
            r'research shows',
            r'studies indicate',
        ]

        sentences = self._extract_sentences(response)
        cited_text = " ".join([c.get("text", "") for c in citations])

        for sentence in sentences:
            # Check if sentence contains fact patterns
            has_fact = any(re.search(pattern, sentence) for pattern in fact_patterns)

            if has_fact and sentence not in cited_text:
                uncited_facts.append(sentence)

        return uncited_facts

    def _calculate_hallucination_risk(
        self,
        grounding_ratio: float,
        citation_coverage: float,
        uncited_fact_count: int,
    ) -> float:
        """Calculate overall hallucination risk score (0-1)."""
        # Weighted risk calculation
        grounding_risk = 1.0 - grounding_ratio
        citation_risk = 1.0 - citation_coverage
        fact_risk = min(uncited_fact_count / 5.0, 1.0)  # Normalize to 0-1

        # Combined risk (weighted average)
        risk = (
            0.5 * grounding_risk +
            0.3 * citation_risk +
            0.2 * fact_risk
        )

        return risk


# Singleton instance
_grounding_service = None


def get_grounding_service(
    min_overlap_ratio: float = 0.3,
    min_citation_coverage: float = 0.7,
) -> GroundingService:
    """Get or create the singleton GroundingService instance."""
    global _grounding_service
    if _grounding_service is None:
        _grounding_service = GroundingService(
            min_overlap_ratio=min_overlap_ratio,
            min_citation_coverage=min_citation_coverage,
        )
    return _grounding_service
