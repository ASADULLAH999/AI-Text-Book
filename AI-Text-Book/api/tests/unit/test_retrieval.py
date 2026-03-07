"""
Unit Tests — RetrievalService
T050 [P] [US1]

Tests cover:
- retrieve() with mock Qdrant results
- rerank() scoring logic
- retrieve_and_rerank() end-to-end
- Edge cases: empty results, score thresholds
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.rag.retrieval import RetrievalService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chunk(
    chunk_id: str = "chunk-1",
    text: str = "This is a sample chunk about neural networks.",
    score: float = 0.85,
    chapter: str = "Chapter 1",
    section: str = "Introduction",
    heading: str = "Overview",
    page_number: int = 1,
) -> dict:
    return {
        "chunk_id": chunk_id,
        "text": text,
        "score": score,
        "metadata": {
            "chapter": chapter,
            "section": section,
            "heading": heading,
            "page_number": page_number,
        },
    }


SAMPLE_CHUNKS = [
    make_chunk("c1", "Neural networks are inspired by the brain.", 0.95, "Chapter 1", "Intro", "Overview", 1),
    make_chunk("c2", "Deep learning uses multiple layers.", 0.88, "Chapter 2", "Deep Learning", "Layers", 5),
    make_chunk("c3", "Backpropagation computes gradients.", 0.82, "Chapter 2", "Training", "Backprop", 8),
    make_chunk("c4", "Activation functions add non-linearity.", 0.78, "Chapter 3", "Activations", "ReLU", 12),
    make_chunk("c5", "Optimizers update model weights.", 0.71, "Chapter 4", "Optimization", "SGD", 20),
]


# ---------------------------------------------------------------------------
# T050-A: RetrievalService instantiation
# ---------------------------------------------------------------------------

class TestRetrievalServiceInit:
    def test_default_parameters(self):
        svc = RetrievalService()
        assert svc.top_k == 20
        assert svc.score_threshold == 0.7
        assert svc.rerank_top_n == 5

    def test_custom_parameters(self):
        svc = RetrievalService(top_k=10, score_threshold=0.8, rerank_top_n=3)
        assert svc.top_k == 10
        assert svc.score_threshold == 0.8
        assert svc.rerank_top_n == 3


# ---------------------------------------------------------------------------
# T050-B: retrieve() — calls Qdrant with correct args
# ---------------------------------------------------------------------------

class TestRetrieve:
    @pytest.fixture
    def service(self):
        return RetrievalService(top_k=5, score_threshold=0.7, rerank_top_n=3)

    @pytest.mark.asyncio
    async def test_retrieve_calls_qdrant(self, service):
        fake_embedding = [0.1] * 1536

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=SAMPLE_CHUNKS)

            results = await service.retrieve(fake_embedding)

        mock_qdrant.search.assert_called_once_with(
            query_vector=fake_embedding,
            limit=service.top_k,
            score_threshold=service.score_threshold,
            filter_conditions=None,
        )
        assert results == SAMPLE_CHUNKS

    @pytest.mark.asyncio
    async def test_retrieve_passes_filters(self, service):
        fake_embedding = [0.2] * 1536
        filters = {"chapter": "Chapter 1"}

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=[SAMPLE_CHUNKS[0]])

            results = await service.retrieve(fake_embedding, filters=filters)

        mock_qdrant.search.assert_called_once_with(
            query_vector=fake_embedding,
            limit=service.top_k,
            score_threshold=service.score_threshold,
            filter_conditions=filters,
        )
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_when_no_results(self, service):
        fake_embedding = [0.0] * 1536

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=[])

            results = await service.retrieve(fake_embedding)

        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_propagates_exception(self, service):
        fake_embedding = [0.1] * 1536

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(side_effect=RuntimeError("Qdrant down"))

            with pytest.raises(RuntimeError, match="Qdrant down"):
                await service.retrieve(fake_embedding)


# ---------------------------------------------------------------------------
# T050-C: rerank() — scoring and ordering
# ---------------------------------------------------------------------------

class TestRerank:
    @pytest.fixture
    def service(self):
        return RetrievalService(rerank_top_n=3)

    def test_rerank_returns_top_n(self, service):
        results = service.rerank(SAMPLE_CHUNKS, "neural networks deep learning")
        assert len(results) == 3

    def test_rerank_empty_chunks(self, service):
        results = service.rerank([], "any query")
        assert results == []

    def test_rerank_adds_score_fields(self, service):
        results = service.rerank(SAMPLE_CHUNKS[:3], "neural networks")
        for chunk in results:
            assert "rerank_score" in chunk
            assert "vector_score" in chunk
            assert "overlap_score" in chunk
            assert "metadata_score" in chunk

    def test_rerank_scores_are_in_valid_range(self, service):
        results = service.rerank(SAMPLE_CHUNKS, "deep learning layers")
        for chunk in results:
            assert 0.0 <= chunk["rerank_score"] <= 1.0
            assert 0.0 <= chunk["vector_score"] <= 1.0
            assert 0.0 <= chunk["overlap_score"] <= 1.0

    def test_rerank_descending_order(self, service):
        results = service.rerank(SAMPLE_CHUNKS, "deep learning")
        scores = [r["rerank_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_rerank_keyword_boost(self, service):
        # Chunk with query keywords should score higher on overlap
        query = "backpropagation gradients"
        results = service.rerank(SAMPLE_CHUNKS, query)
        # chunk "c3" is about backpropagation — it should appear in top 3
        top_ids = [r["chunk_id"] for r in results]
        assert "c3" in top_ids

    def test_rerank_metadata_completeness_matters(self, service):
        # Chunk with full metadata should get metadata_score of 1.0
        full_meta_chunk = make_chunk("full", "test", 0.75, "Ch1", "S1", "H1", 1)
        no_meta_chunk = make_chunk(
            "empty", "test", 0.75,
            chapter="", section="", heading="", page_number=None
        )
        no_meta_chunk["metadata"] = {}

        results = service.rerank([full_meta_chunk, no_meta_chunk], "test")
        assert results[0]["chunk_id"] == "full"

    def test_rerank_preserves_original_chunk_data(self, service):
        results = service.rerank(SAMPLE_CHUNKS[:2], "neural networks")
        for result in results:
            assert "chunk_id" in result
            assert "text" in result
            assert "metadata" in result


# ---------------------------------------------------------------------------
# T050-D: retrieve_and_rerank() — combined flow
# ---------------------------------------------------------------------------

class TestRetrieveAndRerank:
    @pytest.fixture
    def service(self):
        return RetrievalService(top_k=5, score_threshold=0.7, rerank_top_n=3)

    @pytest.mark.asyncio
    async def test_retrieve_and_rerank_returns_reranked_results(self, service):
        fake_embedding = [0.1] * 1536

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=SAMPLE_CHUNKS)

            results = await service.retrieve_and_rerank(
                query="neural networks",
                query_embedding=fake_embedding,
            )

        assert len(results) <= service.rerank_top_n
        for r in results:
            assert "rerank_score" in r

    @pytest.mark.asyncio
    async def test_retrieve_and_rerank_empty_results(self, service):
        fake_embedding = [0.0] * 1536

        with patch("services.rag.retrieval.qdrant_client") as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=[])

            results = await service.retrieve_and_rerank(
                query="something obscure",
                query_embedding=fake_embedding,
            )

        assert results == []
