"""
General Knowledge Mode Service
T071 [US3]

Allows broader answers that go beyond the textbook content.
Opt-in only; visual indicator (amber badge + disclaimer) required in UI.
No grounding or citation requirements — but warnings are encouraged.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GeneralKnowledgeMode:
    """
    General Knowledge mode — allows the LLM to draw on its full training
    data rather than being restricted to retrieved textbook chunks.

    Key characteristics:
    - Vector search still performed (provides context hints), but not required
    - No hallucination-gate refusals
    - Response includes a disclaimer that the answer may extend beyond the text
    - Mode is amber in the UI and gated behind explicit opt-in
    """

    # Disclaimer appended to all General Knowledge responses
    DISCLAIMER = (
        "\n\n---\n*⚠️ This answer may include information beyond the textbook. "
        "Please verify with your primary sources.*"
    )

    def __init__(
        self,
        append_disclaimer: bool = True,
        soft_retrieval: bool = True,
    ):
        """
        Args:
            append_disclaimer: Append the disclaimer to all responses.
            soft_retrieval: When True, vector search results are provided as
                            optional context but the LLM is not grounded to them.
        """
        self.append_disclaimer = append_disclaimer
        self.soft_retrieval = soft_retrieval
        logger.info(
            f"Initialized GeneralKnowledgeMode "
            f"(append_disclaimer={append_disclaimer}, soft_retrieval={soft_retrieval})"
        )

    def build_system_prompt(self, retrieved_chunks: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Build the system prompt for General Knowledge mode.

        Args:
            retrieved_chunks: Optional list of textbook chunks for soft context.

        Returns:
            System prompt string.
        """
        base = (
            "You are a knowledgeable educational assistant. "
            "You may use your general knowledge to answer student questions. "
            "When relevant textbook passages are provided, use them as helpful context, "
            "but do not restrict your answer to those passages only. "
            "Always be accurate and pedagogically helpful."
        )

        if retrieved_chunks:
            context_texts = [c.get("text", "") for c in retrieved_chunks if c.get("text")]
            if context_texts:
                context_block = "\n\n".join(f"[Context]: {t}" for t in context_texts[:3])
                base += f"\n\nRelated textbook context (optional reference):\n{context_block}"

        return base

    def process_response(self, response: str) -> str:
        """
        Post-process the LLM response to append the disclaimer.

        Args:
            response: Raw LLM response text.

        Returns:
            Response with disclaimer appended (if enabled).
        """
        if self.append_disclaimer:
            return response + self.DISCLAIMER
        return response

    def build_response_metadata(
        self,
        chunks_retrieved: int = 0,
        query_length: int = 0,
    ) -> Dict[str, Any]:
        """
        Build metadata for the API response in General Knowledge mode.

        Args:
            chunks_retrieved: Number of chunks retrieved (soft context).
            query_length: Length of the user query.

        Returns:
            Metadata dict for the ChatResponse.
        """
        return {
            "mode": "general_knowledge",
            "grounded": False,
            "disclaimer_shown": self.append_disclaimer,
            "soft_retrieval": self.soft_retrieval,
            "chunks_retrieved": chunks_retrieved,
            "query_length": query_length,
        }

    def get_mode_info(self) -> Dict[str, Any]:
        """Return mode metadata for API responses."""
        return {
            "mode": "general_knowledge",
            "label": "General Knowledge",
            "description": "Broader answers that may extend beyond the textbook",
            "color": "amber",
            "vector_search": self.soft_retrieval,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_general_knowledge_mode: Optional[GeneralKnowledgeMode] = None


def get_general_knowledge_mode(
    append_disclaimer: bool = True,
    soft_retrieval: bool = True,
) -> GeneralKnowledgeMode:
    """Get or create the singleton GeneralKnowledgeMode instance."""
    global _general_knowledge_mode
    if _general_knowledge_mode is None:
        _general_knowledge_mode = GeneralKnowledgeMode(
            append_disclaimer=append_disclaimer,
            soft_retrieval=soft_retrieval,
        )
    return _general_knowledge_mode
