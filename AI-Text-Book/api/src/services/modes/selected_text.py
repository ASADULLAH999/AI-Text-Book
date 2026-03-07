"""
Selected-Text Mode Service
T061 [US2]

Answers questions using ONLY the user-selected text passage —
zero vector searches are performed in this mode.
The selection acts as both context and citation source.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T063 [US2] — Insufficient context refusal template
# ---------------------------------------------------------------------------

INSUFFICIENT_CONTEXT_REFUSAL = (
    "I'm sorry, but the selected text doesn't contain enough information "
    "to answer your question.\n\n"
    "The selected passage is:\n"
    "  • Too short to provide a meaningful answer, OR\n"
    "  • Does not address what you're asking about.\n\n"
    "Try one of these instead:\n"
    "- Select a longer passage that covers your topic\n"
    "- Switch to **Book-Only** mode to search the full textbook\n"
    "- Rephrase your question to match the selected content"
)

EMPTY_SELECTION_REFUSAL = (
    "No text was selected. Please highlight a passage in the textbook "
    "before using 'Ask AI about this'."
)


class SelectedTextMode:
    """
    Selected-Text mode — answers are derived exclusively from
    the user-provided selection context.

    Key invariant: **zero** vector database searches are performed.
    The selection text is treated as the sole retrieved context.
    """

    def __init__(
        self,
        min_selection_tokens: int = 50,
        max_selection_tokens: int = 4000,
        chars_per_token: int = 4,
    ):
        """
        Args:
            min_selection_tokens: Minimum selection size (50 tokens)
            max_selection_tokens: Maximum selection size (4,000 tokens)
            chars_per_token: Characters per token (approximation)
        """
        self.min_selection_tokens = min_selection_tokens
        self.max_selection_tokens = max_selection_tokens
        self.chars_per_token = chars_per_token

        self.min_chars = min_selection_tokens * chars_per_token
        self.max_chars = max_selection_tokens * chars_per_token

        logger.info(
            f"Initialized SelectedTextMode "
            f"(tokens: {min_selection_tokens}–{max_selection_tokens})"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_selection(
        self,
        selection_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate that the selection context is usable.

        Args:
            selection_context: Dict with keys:
                selected_text (str): The highlighted passage
                token_count (int, optional): Client-side estimate
                source_hint (dict, optional): chapter/section hints

        Returns:
            {is_valid: bool, reason: str | None, token_count: int}
        """
        selected_text = selection_context.get("selected_text", "").strip()

        if not selected_text:
            return {
                "is_valid": False,
                "reason": "empty_selection",
                "token_count": 0,
            }

        # Use client token_count if provided, otherwise estimate
        token_count = selection_context.get("token_count") or self._estimate_tokens(
            selected_text
        )

        if token_count < self.min_selection_tokens:
            return {
                "is_valid": False,
                "reason": "too_short",
                "token_count": token_count,
            }

        if token_count > self.max_selection_tokens:
            return {
                "is_valid": False,
                "reason": "too_long",
                "token_count": token_count,
            }

        return {
            "is_valid": True,
            "reason": None,
            "token_count": token_count,
        }

    def build_context_chunk(
        self,
        selection_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert the selection context into a synthetic "chunk" compatible
        with the citation and grounding services.

        This is the only chunk — no vector search is performed.

        Args:
            selection_context: Selection dict from the API request

        Returns:
            A chunk dict compatible with CitationService and GroundingService
        """
        selected_text = selection_context.get("selected_text", "")
        source_hint = selection_context.get("source_hint", {})
        token_count = selection_context.get("token_count") or self._estimate_tokens(
            selected_text
        )

        chunk = {
            "chunk_id": "selected_text_ctx",
            "text": selected_text,
            "score": 1.0,  # Perfect relevance — it's exactly what the user chose
            "rerank_score": 1.0,
            "metadata": {
                "chapter": source_hint.get("chapter", "Selected Passage"),
                "section": source_hint.get("section", "User Selection"),
                "heading": "Selected Text",
                "page_number": None,
                "selection_mode": True,
                "token_count": token_count,
            },
        }

        logger.debug(
            f"Built selection chunk: {token_count} tokens, "
            f"chapter={chunk['metadata']['chapter']}"
        )
        return chunk

    def create_refusal_response(
        self,
        reason: str = "insufficient_context",
    ) -> Dict[str, Any]:
        """
        Create a refusal response for invalid selections.

        Args:
            reason: "empty_selection" | "too_short" | "too_long" | "insufficient_context"

        Returns:
            Standard refusal response dict
        """
        if reason == "empty_selection":
            message = EMPTY_SELECTION_REFUSAL
        else:
            message = INSUFFICIENT_CONTEXT_REFUSAL

        response = {
            "message": message,
            "refused": True,
            "reason": reason,
            "citations": [],
            "metadata": {
                "mode": "selected_text",
                "refused": True,
                "refusal_reason": reason,
                "vector_searches_performed": 0,
            },
        }

        logger.info(f"Created Selected-Text refusal: {reason}")
        return response

    def process_query(
        self,
        query: str,
        selection_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process a query against the selected text (no vector search).

        This method validates the selection, builds the synthetic context chunk,
        and returns metadata for the pipeline to generate a response.

        The actual LLM call is handled by the orchestrator; this method
        provides the grounding context.

        Args:
            query: The user's question
            selection_context: Selection dict from the API request

        Returns:
            {
                should_refuse: bool,
                refusal_response: dict | None,
                context_chunks: list[dict],
                metadata: dict,
            }
        """
        # Validate selection
        validation = self.validate_selection(selection_context)

        if not validation["is_valid"]:
            logger.warning(
                f"Selected-Text mode refused: {validation['reason']}"
            )
            return {
                "should_refuse": True,
                "refusal_response": self.create_refusal_response(
                    validation["reason"]
                ),
                "context_chunks": [],
                "metadata": {
                    "mode": "selected_text",
                    "vector_searches_performed": 0,
                    "refusal_reason": validation["reason"],
                },
            }

        # Build the single context chunk from selection
        context_chunk = self.build_context_chunk(selection_context)

        logger.info(
            f"Selected-Text mode processing query: {query[:80]}... "
            f"(selection: {validation['token_count']} tokens, "
            f"vector_searches=0)"
        )

        return {
            "should_refuse": False,
            "refusal_response": None,
            "context_chunks": [context_chunk],
            "metadata": {
                "mode": "selected_text",
                "vector_searches_performed": 0,  # T068: invariant
                "selection_token_count": validation["token_count"],
                "query_length": len(query),
            },
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from character count."""
        return max(1, len(text.strip()) // self.chars_per_token)

    def get_mode_info(self) -> Dict[str, Any]:
        """Return mode metadata for API responses."""
        return {
            "mode": "selected_text",
            "label": "Selected Text",
            "description": "Answers derived exclusively from the selected text passage",
            "color": "purple",
            "vector_search": False,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_selected_text_mode: Optional[SelectedTextMode] = None


def get_selected_text_mode(
    min_selection_tokens: int = 50,
    max_selection_tokens: int = 4000,
) -> SelectedTextMode:
    """Get or create the singleton SelectedTextMode instance."""
    global _selected_text_mode
    if _selected_text_mode is None:
        _selected_text_mode = SelectedTextMode(
            min_selection_tokens=min_selection_tokens,
            max_selection_tokens=max_selection_tokens,
        )
    return _selected_text_mode
