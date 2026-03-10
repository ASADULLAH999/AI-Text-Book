"""
Book-Only Mode Service
Implements strict grounding logic to ensure responses are derived exclusively from textbook content.
"""

from typing import List, Dict, Any, Optional
import logging
from services.rag.embedding import get_query_embedding_service
from services.rag.retrieval import get_retrieval_service
from services.rag.grounding import get_grounding_service
from services.citation_service import get_citation_service

logger = logging.getLogger(__name__)


class BookOnlyMode:
    """
    Book-Only mode that ensures all responses are strictly grounded in textbook content.

    This mode:
    1. Only retrieves from textbook chunks
    2. Validates all responses against retrieved context
    3. Refuses to answer if insufficient context
    4. Provides citations for all claims
    """

    # Refusal message template
    REFUSAL_MESSAGE = (
        "Sorry, I could not find this in the textbook."
    )

    def __init__(
        self,
        min_retrieval_score: float = 0.2,
        min_grounding_ratio: float = 0.2,
        min_citation_coverage: float = 0.4,
        require_citations: bool = True,
    ):
        """
        Initialize Book-Only mode.

        Args:
            min_retrieval_score: Minimum score for retrieved chunks
            min_grounding_ratio: Minimum grounding ratio required
            min_citation_coverage: Minimum citation coverage required
            require_citations: Whether citations are mandatory
        """
        self.min_retrieval_score = min_retrieval_score
        self.min_grounding_ratio = min_grounding_ratio
        self.min_citation_coverage = min_citation_coverage
        self.require_citations = require_citations

        # Initialize services
        self.embedding_service = get_query_embedding_service()
        self.retrieval_service = get_retrieval_service(
            top_k=30,
            score_threshold=min_retrieval_score,
            rerank_top_n=8,
        )
        self.grounding_service = get_grounding_service()
        self.citation_service = get_citation_service()

        logger.info(
            f"Initialized BookOnlyMode "
            f"(score≥{min_retrieval_score}, grounding≥{min_grounding_ratio})"
        )

    async def should_refuse(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if the query should be refused based on retrieval quality.

        Args:
            query: User query
            retrieved_chunks: Retrieved context chunks

        Returns:
            Tuple of (should_refuse, refusal_reason)
        """
        # Check 1: No chunks retrieved
        if not retrieved_chunks:
            logger.warning("No chunks retrieved - refusing query")
            return True, "No relevant content found in textbook"

        # Check 2: All chunks below score threshold.
        # Use raw vector_score (not rerank_score) — rerank_score is a weighted
        # composite (0.6*vector + 0.3*overlap + 0.1*meta) that is structurally
        # lower than vector similarity alone, so comparing it against
        # min_retrieval_score would refuse valid retrievals.
        max_score = max(
            chunk.get("vector_score", chunk.get("score", 0.0))
            for chunk in retrieved_chunks
        )
        if max_score < self.min_retrieval_score:
            logger.warning(
                f"Low retrieval scores (max={max_score:.3f}) - refusing query"
            )
            return True, "Insufficient relevance to textbook content"

        # Check 3: Very short/trivial chunks
        total_text = " ".join([chunk.get("text", "") for chunk in retrieved_chunks])
        if len(total_text.split()) < 50:
            logger.warning("Insufficient context length - refusing query")
            return True, "Insufficient textbook content retrieved"

        # Query is acceptable
        return False, None

    def validate_response(
        self,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate that response meets Book-Only mode requirements.

        Args:
            response: Generated response
            retrieved_chunks: Retrieved context chunks
            citations: Generated citations

        Returns:
            Validation result with pass/fail and reasons
        """
        logger.debug("Validating response for Book-Only mode")

        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {},
        }

        # Validate grounding
        grounding_result = self.grounding_service.validate_grounding(
            response, retrieved_chunks
        )
        validation_result["metrics"]["grounding_ratio"] = grounding_result[
            "grounding_ratio"
        ]

        if grounding_result["grounding_ratio"] < self.min_grounding_ratio:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Grounding ratio {grounding_result['grounding_ratio']:.2%} "
                f"below threshold {self.min_grounding_ratio:.2%}"
            )

        # Detect hallucinations
        hallucination_result = self.grounding_service.detect_hallucination(
            response, retrieved_chunks, citations
        )
        validation_result["metrics"]["hallucination_risk"] = hallucination_result[
            "hallucination_risk"
        ]

        if not hallucination_result["is_safe"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"High hallucination risk: {hallucination_result['hallucination_risk']:.2%}"
            )

        # Validate citations
        if self.require_citations and not citations:
            validation_result["is_valid"] = False
            validation_result["errors"].append("No citations provided")

        validation_result["metrics"]["citation_count"] = len(citations)

        # Log validation result
        if validation_result["is_valid"]:
            logger.info("Response passed Book-Only validation")
        else:
            logger.warning(
                f"Response failed Book-Only validation: {validation_result['errors']}"
            )

        return validation_result

    def create_refusal_response(
        self,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a refusal response.

        Args:
            reason: Optional specific reason for refusal

        Returns:
            Refusal response object
        """
        response = {
            "message": self.REFUSAL_MESSAGE,
            "refused": True,
            "reason": reason or "Insufficient textbook content",
            "citations": [],
            "metadata": {
                "mode": "book_only",
                "refused": True,
            },
        }

        logger.info(f"Created refusal response: {reason}")
        return response


# Singleton instance
_book_only_mode = None


def get_book_only_mode(
    min_retrieval_score: float = 0.2,
    min_grounding_ratio: float = 0.2,
    min_citation_coverage: float = 0.4,
) -> BookOnlyMode:
    """Get or create the singleton BookOnlyMode instance."""
    global _book_only_mode
    if _book_only_mode is None:
        _book_only_mode = BookOnlyMode(
            min_retrieval_score=min_retrieval_score,
            min_grounding_ratio=min_grounding_ratio,
            min_citation_coverage=min_citation_coverage,
        )
    return _book_only_mode
