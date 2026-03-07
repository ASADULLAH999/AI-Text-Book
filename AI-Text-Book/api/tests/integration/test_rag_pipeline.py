"""
Integration Tests — RAG Pipeline End-to-End
T053 [US1]

Tests cover:
- Full pipeline: embed → retrieve → rerank → citations → response
- Book-Only mode refusal logic
- Error handling and fallback behavior
- Citation grounding validation in the pipeline
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chunk(
    chunk_id: str,
    text: str,
    score: float = 0.85,
    chapter: str = "Chapter 1",
    section: str = "Introduction",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "text": text,
        "score": score,
        "metadata": {
            "chapter": chapter,
            "section": section,
            "heading": "Overview",
            "page_number": 1,
        },
    }


NEURAL_NETWORK_CHUNKS = [
    make_chunk("c1", "Neural networks are computational models inspired by the brain.", 0.95, "Chapter 1", "Intro"),
    make_chunk("c2", "Deep learning uses multiple stacked layers for feature extraction.", 0.88, "Chapter 2", "Deep Learning"),
    make_chunk("c3", "Backpropagation algorithm computes gradients by chain rule.", 0.82, "Chapter 2", "Training"),
    make_chunk("c4", "Activation functions like ReLU add non-linearity to networks.", 0.78, "Chapter 3", "Activations"),
    make_chunk("c5", "Optimizers such as SGD and Adam update weights during training.", 0.71, "Chapter 4", "Optimization"),
]

FAKE_EMBEDDING = [0.1] * 1536


# ---------------------------------------------------------------------------
# T053-A: RAG pipeline imports and initialization
# ---------------------------------------------------------------------------

class TestPipelineInit:
    def test_orchestrator_can_be_imported(self):
        from services.rag.orchestrator import RAGOrchestrator
        assert RAGOrchestrator is not None

    def test_retrieval_service_can_be_imported(self):
        from services.rag.retrieval import RetrievalService
        assert RetrievalService is not None

    def test_grounding_service_can_be_imported(self):
        from services.rag.grounding import GroundingService
        assert GroundingService is not None

    def test_citation_service_can_be_imported(self):
        from services.citation_service import CitationService
        assert CitationService is not None


# ---------------------------------------------------------------------------
# T053-B: RetrievalService → CitationService pipeline
# ---------------------------------------------------------------------------

class TestRetrievalToCitation:
    """Verify chunks retrieved from vector DB produce well-formed citations."""

    def test_chunks_produce_valid_citations(self):
        from services.rag.retrieval import RetrievalService
        from services.citation_service import CitationService

        retrieval = RetrievalService()
        citation_svc = CitationService()

        # Simulate reranked chunks
        reranked = retrieval.rerank(NEURAL_NETWORK_CHUNKS, "neural network training")

        # Generate citations from reranked results
        citations = citation_svc.generate_citations(reranked)

        assert len(citations) > 0
        for citation in citations:
            validation = citation_svc.validate_citation(citation)
            assert validation["is_valid"], f"Invalid citation: {validation['errors']}"

    def test_reranked_chunks_preserve_metadata(self):
        from services.rag.retrieval import RetrievalService

        svc = RetrievalService(rerank_top_n=3)
        reranked = svc.rerank(NEURAL_NETWORK_CHUNKS, "backpropagation gradients")

        for chunk in reranked:
            assert chunk["metadata"].get("chapter")
            assert chunk["metadata"].get("section")

    def test_citation_count_matches_chunk_count(self):
        from services.rag.retrieval import RetrievalService
        from services.citation_service import CitationService

        retrieval = RetrievalService(rerank_top_n=3)
        citation_svc = CitationService()

        reranked = retrieval.rerank(NEURAL_NETWORK_CHUNKS, "deep learning")
        citations = citation_svc.generate_citations(reranked)

        assert len(citations) == len(reranked)


# ---------------------------------------------------------------------------
# T053-C: CitationService → GroundingService pipeline
# ---------------------------------------------------------------------------

class TestCitationToGrounding:
    """Verify citations are used correctly in grounding validation."""

    def test_grounding_with_valid_citations(self):
        from services.citation_service import CitationService
        from services.rag.grounding import GroundingService

        citation_svc = CitationService()
        grounding = GroundingService(min_overlap_ratio=0.2)

        citations = citation_svc.generate_citations(NEURAL_NETWORK_CHUNKS[:3])
        response = (
            "Neural networks are inspired by the brain and use backpropagation "
            "to compute gradients for training. Deep learning employs multiple layers."
        )

        result = grounding.validate_grounding(response, NEURAL_NETWORK_CHUNKS[:3])
        assert result["is_grounded"] is True

    def test_hallucination_detection_with_citations(self):
        from services.citation_service import CitationService
        from services.rag.grounding import GroundingService

        citation_svc = CitationService()
        grounding = GroundingService()

        citations = citation_svc.generate_citations(NEURAL_NETWORK_CHUNKS[:3])
        response = "Neural networks use layers to learn representations."

        result = grounding.detect_hallucination(response, NEURAL_NETWORK_CHUNKS[:3], citations)
        assert 0.0 <= result["hallucination_risk"] <= 1.0
        assert isinstance(result["is_safe"], bool)

    def test_deduplication_does_not_break_grounding(self):
        from services.citation_service import CitationService
        from services.rag.grounding import GroundingService

        citation_svc = CitationService()
        grounding = GroundingService(min_overlap_ratio=0.2)

        # Duplicate chunk
        dup_chunks = NEURAL_NETWORK_CHUNKS[:2] + [NEURAL_NETWORK_CHUNKS[0]]
        citations = citation_svc.generate_citations(dup_chunks)
        deduped = citation_svc.deduplicate_citations(citations)

        response = "Neural networks are computational models."
        result = grounding.validate_grounding(response, dup_chunks)

        assert result["total_sentences"] > 0


# ---------------------------------------------------------------------------
# T053-D: Full RAGOrchestrator pipeline with mocks
# ---------------------------------------------------------------------------

class TestRAGOrchestratorPipeline:
    """End-to-end orchestrator tests with external services mocked."""

    @pytest.mark.asyncio
    async def test_successful_pipeline_response_structure(self):
        from services.rag.orchestrator import RAGOrchestrator

        with patch("services.rag.orchestrator.get_query_embedding_service") as mock_embed_factory, \
             patch("services.rag.orchestrator.get_retrieval_service") as mock_retrieval_factory, \
             patch("services.rag.orchestrator.get_book_only_mode") as mock_mode_factory, \
             patch("services.rag.orchestrator.get_citation_service") as mock_citation_factory:

            # Mock embedding
            mock_embed = AsyncMock()
            mock_embed.embed_query = AsyncMock(return_value=FAKE_EMBEDDING)
            mock_embed_factory.return_value = mock_embed

            # Mock retrieval
            mock_retrieval = MagicMock()
            mock_retrieval.retrieve_and_rerank = AsyncMock(return_value=NEURAL_NETWORK_CHUNKS[:3])
            mock_retrieval_factory.return_value = mock_retrieval

            # Mock book-only mode
            mock_mode = MagicMock()
            mock_mode.should_refuse = AsyncMock(return_value=(False, None))
            mock_mode.validate_response = MagicMock(return_value={"is_valid": True, "errors": []})
            mock_mode_factory.return_value = mock_mode

            # Mock citation service
            from services.citation_service import CitationService
            real_citation = CitationService()
            mock_citation_factory.return_value = real_citation

            orchestrator = RAGOrchestrator(mode="book_only")
            response = await orchestrator.process_query("What are neural networks?")

        assert "message" in response
        assert "citations" in response
        assert "metadata" in response
        assert response["refused"] is False

    @pytest.mark.asyncio
    async def test_pipeline_returns_citations(self):
        from services.rag.orchestrator import RAGOrchestrator

        with patch("services.rag.orchestrator.get_query_embedding_service") as mock_embed_factory, \
             patch("services.rag.orchestrator.get_retrieval_service") as mock_retrieval_factory, \
             patch("services.rag.orchestrator.get_book_only_mode") as mock_mode_factory, \
             patch("services.rag.orchestrator.get_citation_service") as mock_citation_factory:

            mock_embed = AsyncMock()
            mock_embed.embed_query = AsyncMock(return_value=FAKE_EMBEDDING)
            mock_embed_factory.return_value = mock_embed

            mock_retrieval = MagicMock()
            mock_retrieval.retrieve_and_rerank = AsyncMock(return_value=NEURAL_NETWORK_CHUNKS[:3])
            mock_retrieval_factory.return_value = mock_retrieval

            mock_mode = MagicMock()
            mock_mode.should_refuse = AsyncMock(return_value=(False, None))
            mock_mode.validate_response = MagicMock(return_value={"is_valid": True, "errors": []})
            mock_mode_factory.return_value = mock_mode

            from services.citation_service import CitationService
            mock_citation_factory.return_value = CitationService()

            orchestrator = RAGOrchestrator(mode="book_only")
            response = await orchestrator.process_query("How does backpropagation work?")

        assert len(response["citations"]) == 3

    @pytest.mark.asyncio
    async def test_pipeline_refuses_when_no_relevant_chunks(self):
        from services.rag.orchestrator import RAGOrchestrator

        with patch("services.rag.orchestrator.get_query_embedding_service") as mock_embed_factory, \
             patch("services.rag.orchestrator.get_retrieval_service") as mock_retrieval_factory, \
             patch("services.rag.orchestrator.get_book_only_mode") as mock_mode_factory, \
             patch("services.rag.orchestrator.get_citation_service") as mock_citation_factory:

            mock_embed = AsyncMock()
            mock_embed.embed_query = AsyncMock(return_value=FAKE_EMBEDDING)
            mock_embed_factory.return_value = mock_embed

            mock_retrieval = MagicMock()
            mock_retrieval.retrieve_and_rerank = AsyncMock(return_value=[])
            mock_retrieval_factory.return_value = mock_retrieval

            mock_mode = MagicMock()
            mock_mode.should_refuse = AsyncMock(return_value=(True, "Insufficient context"))
            mock_mode.create_refusal_response = MagicMock(return_value={
                "message": "Cannot answer",
                "citations": [],
                "refused": True,
                "metadata": {"mode": "book_only"},
            })
            mock_mode_factory.return_value = mock_mode

            from services.citation_service import CitationService
            mock_citation_factory.return_value = CitationService()

            orchestrator = RAGOrchestrator(mode="book_only")
            response = await orchestrator.process_query("Who won the 2025 World Cup?")

        assert response["refused"] is True

    @pytest.mark.asyncio
    async def test_pipeline_handles_embedding_failure(self):
        from services.rag.orchestrator import RAGOrchestrator

        with patch("services.rag.orchestrator.get_query_embedding_service") as mock_embed_factory, \
             patch("services.rag.orchestrator.get_retrieval_service") as mock_retrieval_factory, \
             patch("services.rag.orchestrator.get_book_only_mode") as mock_mode_factory, \
             patch("services.rag.orchestrator.get_citation_service") as mock_citation_factory:

            mock_embed = AsyncMock()
            mock_embed.embed_query = AsyncMock(side_effect=RuntimeError("OpenAI unavailable"))
            mock_embed_factory.return_value = mock_embed

            mock_retrieval_factory.return_value = MagicMock()
            mock_mode_factory.return_value = MagicMock()

            from services.citation_service import CitationService
            mock_citation_factory.return_value = CitationService()

            orchestrator = RAGOrchestrator(mode="book_only")
            response = await orchestrator.process_query("Test query")

        # Should return error response, not raise
        assert "error" in response or response.get("refused") is True


# ---------------------------------------------------------------------------
# T053-E: Grounding constraints in pipeline
# ---------------------------------------------------------------------------

class TestGroundingConstraints:
    """Verify that the grounding service correctly gates pipeline output."""

    def test_grounding_threshold_enforced(self):
        from services.rag.grounding import GroundingService

        # Strict threshold
        strict_svc = GroundingService(min_overlap_ratio=0.9)
        # Permissive threshold
        permissive_svc = GroundingService(min_overlap_ratio=0.1)

        chunks = [make_chunk("c1", "Neural networks learn from data.", 0.9)]
        response = "Neural networks learn representations."

        strict_result = strict_svc.validate_grounding(response, chunks)
        permissive_result = permissive_svc.validate_grounding(response, chunks)

        # Permissive should be more lenient
        assert permissive_result["grounding_ratio"] >= strict_result["grounding_ratio"] or \
               permissive_result["is_grounded"] >= strict_result["is_grounded"]

    def test_citation_coverage_affects_hallucination_risk(self):
        from services.citation_service import CitationService
        from services.rag.grounding import GroundingService

        svc = CitationService()
        grounding = GroundingService()

        chunks = NEURAL_NETWORK_CHUNKS[:3]
        citations = svc.generate_citations(chunks)
        response = "Neural networks are computational models."

        result_with_citations = grounding.detect_hallucination(response, chunks, citations)
        result_no_citations = grounding.detect_hallucination(response, chunks, [])

        # More citations should lower risk or keep it equal
        assert result_with_citations["hallucination_risk"] <= \
               result_no_citations["hallucination_risk"] + 0.1  # Allow small tolerance
