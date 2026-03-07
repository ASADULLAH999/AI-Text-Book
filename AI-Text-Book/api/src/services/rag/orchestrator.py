"""
RAG Orchestrator
Coordinates the end-to-end RAG pipeline for question answering.
Supports three modes: book_only, selected_text, general_knowledge.
"""

from typing import Dict, Any, Optional, List
import logging
from services.rag.embedding import get_query_embedding_service
from services.rag.retrieval import get_retrieval_service
from services.citation_service import get_citation_service
from services.modes.book_only import get_book_only_mode
from services.modes.selected_text import get_selected_text_mode
from services.modes.general_knowledge import get_general_knowledge_mode
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Orchestrates the complete RAG pipeline.

    Supports three modes per-request:
      book_only        — strict grounding, citations required
      selected_text    — zero vector search, selection context only
      general_knowledge — soft retrieval, no grounding gate, disclaimer appended
    """

    def __init__(self):
        self.embedding_service = get_query_embedding_service()
        self.retrieval_service = get_retrieval_service()
        self.citation_service = get_citation_service()
        self.llm_service = get_llm_service()
        logger.info("Initialized RAGOrchestrator (mode-agnostic)")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def process_query(
        self,
        query: str,
        mode: str = "book_only",
        filters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        selection_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user query through the appropriate RAG pipeline.

        Args:
            query: User question
            mode: "book_only" | "selected_text" | "general_knowledge"
            filters: Optional metadata filters (chapter, section, etc.)
            metadata: Optional request metadata (tone, conversation_id, …)
            selection_context: Required when mode == "selected_text"

        Returns:
            Response dict with message, citations, refused, metadata
        """
        logger.info(f"Processing query (mode={mode}): {query[:100]}...")
        tone = (metadata or {}).get("tone")

        try:
            if mode == "book_only":
                return await self._process_book_only(query, tone, filters, metadata)
            elif mode == "selected_text":
                return await self._process_selected_text(query, tone, selection_context, metadata)
            elif mode == "general_knowledge":
                return await self._process_general_knowledge(query, tone, filters, metadata)
            else:
                raise ValueError(f"Unsupported mode: {mode}")

        except Exception as e:
            logger.error(f"Error processing query (mode={mode}): {e}", exc_info=True)
            return {
                "message": "An error occurred while processing your question. Please try again.",
                "error": str(e),
                "citations": [],
                "refused": True,
                "metadata": {"mode": mode, "error": True},
            }

    # ------------------------------------------------------------------
    # Mode pipelines
    # ------------------------------------------------------------------

    async def _process_book_only(
        self,
        query: str,
        tone: Optional[str],
        filters: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Strict textbook grounding — citations required, grounding validated."""
        mode_service = get_book_only_mode()

        # 1. Embed query
        query_embedding = await self.embedding_service.embed_query(query)

        # 2. Retrieve + rerank
        retrieved_chunks = await self.retrieval_service.retrieve_and_rerank(
            query=query,
            query_embedding=query_embedding,
            filters=filters,
        )

        # 3. Refusal check
        should_refuse, refusal_reason = await mode_service.should_refuse(query, retrieved_chunks)
        if should_refuse:
            logger.warning(f"book_only refusing: {refusal_reason}")
            return mode_service.create_refusal_response(refusal_reason)

        # 4. Citations
        citations = self.citation_service.generate_citations(retrieved_chunks)
        citations = self.citation_service.deduplicate_citations(citations)

        # 5. LLM generation
        response_text = await self.llm_service.generate(
            query=query, chunks=retrieved_chunks, mode="book_only", tone=tone
        )

        # 6. Grounding validation
        validation = mode_service.validate_response(response_text, retrieved_chunks, citations)
        if not validation["is_valid"]:
            logger.warning(f"book_only validation failed: {validation['errors']}")
            return mode_service.create_refusal_response("Generated response failed validation")

        return self._build_response(response_text, citations, "book_only", query,
                                    len(retrieved_chunks), metadata)

    async def _process_selected_text(
        self,
        query: str,
        tone: Optional[str],
        selection_context: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Zero vector search — answers derived exclusively from selected passage."""
        mode_service = get_selected_text_mode()

        # Validate selection and build synthetic chunk (no vector search)
        result = mode_service.process_query(query, selection_context or {})
        if result["should_refuse"]:
            return result["refusal_response"]

        chunks = result["context_chunks"]

        # Citations from the single selection chunk
        citations = self.citation_service.generate_citations(chunks)

        # LLM generation (grounded to selection)
        response_text = await self.llm_service.generate(
            query=query, chunks=chunks, mode="selected_text", tone=tone
        )

        return self._build_response(response_text, citations, "selected_text", query,
                                    len(chunks), metadata,
                                    extra={"vector_searches_performed": 0})

    async def _process_general_knowledge(
        self,
        query: str,
        tone: Optional[str],
        filters: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Soft retrieval — LLM may draw on general knowledge, disclaimer appended."""
        mode_service = get_general_knowledge_mode()

        # 1. Embed query
        query_embedding = await self.embedding_service.embed_query(query)

        # 2. Soft retrieval (low threshold, no refusal if empty)
        retrieved_chunks = await self.retrieval_service.retrieve_and_rerank(
            query=query,
            query_embedding=query_embedding,
            filters=filters,
        )

        # 3. Citations (soft — may be empty)
        citations = self.citation_service.generate_citations(retrieved_chunks)
        citations = self.citation_service.deduplicate_citations(citations)

        # 4. LLM generation (general knowledge prompt with optional soft context)
        response_text = await self.llm_service.generate(
            query=query, chunks=retrieved_chunks, mode="general_knowledge", tone=tone
        )

        # 5. Append disclaimer
        response_text = mode_service.process_response(response_text)

        return self._build_response(response_text, citations, "general_knowledge", query,
                                    len(retrieved_chunks), metadata,
                                    extra={"disclaimer_shown": True})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_response(
        self,
        message: str,
        citations: List[Dict[str, Any]],
        mode: str,
        query: str,
        retrieved_chunks: int,
        metadata: Optional[Dict[str, Any]],
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response_meta = {
            "mode": mode,
            "query": query,
            "retrieved_chunks": retrieved_chunks,
            "timestamp": (metadata or {}).get("timestamp"),
            "tone": (metadata or {}).get("tone"),
        }
        if extra:
            response_meta.update(extra)

        logger.info(f"Query processed (mode={mode}, citations={len(citations)})")
        return {
            "message": message,
            "citations": citations,
            "refused": False,
            "metadata": response_meta,
        }


# Singleton
_rag_orchestrator: Optional[RAGOrchestrator] = None


def get_rag_orchestrator(mode: str = "book_only") -> RAGOrchestrator:
    """Get or create the singleton RAGOrchestrator (mode is handled per-request)."""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator()
    return _rag_orchestrator
