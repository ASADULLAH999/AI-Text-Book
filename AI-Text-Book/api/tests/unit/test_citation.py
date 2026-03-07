"""
Unit Tests — CitationService
T052 [P] [US1]

Tests cover:
- generate_citations(): full citation list from chunks
- _create_citation(): single citation object structure
- _create_preview(): text truncation at word boundaries
- validate_citation(): required field and content checks
- format_citation_text(): APA, inline, default formats
- deduplicate_citations(): dedup by chunk_id
"""

import pytest
from services.citation_service import CitationService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chunk(
    chunk_id: str = "chunk-1",
    text: str = "Neural networks are computational models.",
    score: float = 0.85,
    chapter: str = "Chapter 1",
    section: str = "Introduction",
    heading: str = "Overview",
    page_number: int = 1,
    rerank_score: float | None = None,
) -> dict:
    chunk = {
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
    if rerank_score is not None:
        chunk["rerank_score"] = rerank_score
    return chunk


SAMPLE_CHUNKS = [
    make_chunk("c1", "Neural networks are inspired by biological neurons.", 0.95, "Chapter 1", "Intro", "Overview", 1, 0.92),
    make_chunk("c2", "Deep learning uses multiple stacked layers.", 0.88, "Chapter 2", "Layers", "Dense Layers", 5, 0.85),
    make_chunk("c3", "Backpropagation computes gradients.", 0.80, "Chapter 2", "Training", "Backprop", 8, 0.78),
]


# ---------------------------------------------------------------------------
# T052-A: CitationService instantiation
# ---------------------------------------------------------------------------

class TestCitationServiceInit:
    def test_instantiation_succeeds(self):
        svc = CitationService()
        assert svc is not None


# ---------------------------------------------------------------------------
# T052-B: generate_citations()
# ---------------------------------------------------------------------------

class TestGenerateCitations:
    @pytest.fixture
    def service(self):
        return CitationService()

    def test_generates_one_citation_per_chunk(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        assert len(citations) == len(SAMPLE_CHUNKS)

    def test_empty_chunks_returns_empty(self, service):
        citations = service.generate_citations([])
        assert citations == []

    def test_citations_have_sequential_numbers(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        for i, citation in enumerate(citations):
            assert citation["number"] == i + 1

    def test_citation_ids_are_unique(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        ids = [c["id"] for c in citations]
        assert len(ids) == len(set(ids))

    def test_citation_preserves_chunk_id(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        for chunk, citation in zip(SAMPLE_CHUNKS, citations):
            assert citation["chunk_id"] == chunk["chunk_id"]

    def test_citation_preserves_text(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        for chunk, citation in zip(SAMPLE_CHUNKS, citations):
            # preview is truncated text; original text should be present
            assert citation["text"] == chunk["text"]

    def test_citation_source_structure(self, service):
        citations = service.generate_citations([SAMPLE_CHUNKS[0]])
        source = citations[0]["source"]
        assert "chapter" in source
        assert "section" in source
        assert "heading" in source
        assert "page_number" in source

    def test_citation_source_values(self, service):
        citations = service.generate_citations([SAMPLE_CHUNKS[0]])
        source = citations[0]["source"]
        assert source["chapter"] == "Chapter 1"
        assert source["section"] == "Intro"
        assert source["page_number"] == 1

    def test_citation_uses_rerank_score_when_present(self, service):
        # When rerank_score exists, it should be used over raw score
        chunk = make_chunk("c1", "test", 0.80, rerank_score=0.92)
        citations = service.generate_citations([chunk])
        assert citations[0]["score"] == 0.92

    def test_citation_falls_back_to_score(self, service):
        # No rerank_score → use base score
        chunk = make_chunk("c1", "test", 0.80, rerank_score=None)
        citations = service.generate_citations([chunk])
        assert citations[0]["score"] == 0.80

    def test_citation_has_timestamp(self, service):
        citations = service.generate_citations([SAMPLE_CHUNKS[0]])
        assert "timestamp" in citations[0]
        assert citations[0]["timestamp"] is not None

    def test_citation_has_preview(self, service):
        citations = service.generate_citations([SAMPLE_CHUNKS[0]])
        assert "preview" in citations[0]
        assert isinstance(citations[0]["preview"], str)


# ---------------------------------------------------------------------------
# T052-C: _create_preview()
# ---------------------------------------------------------------------------

class TestCreatePreview:
    @pytest.fixture
    def service(self):
        return CitationService()

    def test_short_text_unchanged(self, service):
        text = "Short text."
        assert service._create_preview(text, max_length=200) == text

    def test_long_text_truncated(self, service):
        text = "word " * 100  # 500 chars
        preview = service._create_preview(text, max_length=50)
        assert len(preview) <= 53  # 50 + up to 3 for "..."
        assert preview.endswith("...")

    def test_truncation_at_word_boundary(self, service):
        text = "The quick brown fox jumps over the lazy dog " * 5
        preview = service._create_preview(text, max_length=30)
        # Should not cut in the middle of a word
        assert "..." in preview
        non_ellipsis = preview[:-3]
        assert not non_ellipsis.endswith(" ")  # ends at word boundary

    def test_empty_text_returns_empty(self, service):
        assert service._create_preview("") == ""

    def test_exactly_max_length_not_truncated(self, service):
        text = "a" * 150
        preview = service._create_preview(text, max_length=150)
        assert preview == text


# ---------------------------------------------------------------------------
# T052-D: validate_citation()
# ---------------------------------------------------------------------------

class TestValidateCitation:
    @pytest.fixture
    def service(self):
        return CitationService()

    @pytest.fixture
    def valid_citation(self, service):
        return service._create_citation(SAMPLE_CHUNKS[0], 1)

    def test_valid_citation_passes(self, service, valid_citation):
        result = service.validate_citation(valid_citation)
        assert result["is_valid"] is True
        assert result["errors"] == []

    def test_missing_required_field_fails(self, service, valid_citation):
        del valid_citation["chunk_id"]
        result = service.validate_citation(valid_citation)
        assert result["is_valid"] is False
        assert any("chunk_id" in e for e in result["errors"])

    def test_missing_chapter_fails(self, service, valid_citation):
        valid_citation["source"]["chapter"] = ""
        result = service.validate_citation(valid_citation)
        assert result["is_valid"] is False

    def test_missing_section_fails(self, service, valid_citation):
        valid_citation["source"]["section"] = ""
        result = service.validate_citation(valid_citation)
        assert result["is_valid"] is False

    def test_empty_text_fails(self, service, valid_citation):
        valid_citation["text"] = "   "
        result = service.validate_citation(valid_citation)
        assert result["is_valid"] is False

    def test_result_structure(self, service, valid_citation):
        result = service.validate_citation(valid_citation)
        assert "is_valid" in result
        assert "errors" in result


# ---------------------------------------------------------------------------
# T052-E: format_citation_text()
# ---------------------------------------------------------------------------

class TestFormatCitationText:
    @pytest.fixture
    def service(self):
        return CitationService()

    @pytest.fixture
    def citation(self, service):
        return service._create_citation(SAMPLE_CHUNKS[0], 1)

    def test_apa_format_includes_chapter_and_section(self, service, citation):
        formatted = service.format_citation_text(citation, "apa")
        assert "Chapter 1" in formatted
        assert "Intro" in formatted

    def test_apa_format_includes_page_when_present(self, service, citation):
        formatted = service.format_citation_text(citation, "apa")
        assert "Page 1" in formatted

    def test_inline_format_uses_brackets(self, service, citation):
        formatted = service.format_citation_text(citation, "inline")
        assert formatted.startswith("[")
        assert formatted.endswith("]")
        assert "Chapter 1" in formatted

    def test_default_format_uses_pipe(self, service, citation):
        formatted = service.format_citation_text(citation, "default")
        assert "|" in formatted

    def test_unknown_format_falls_back_to_default(self, service, citation):
        formatted = service.format_citation_text(citation, "unknown_style")
        assert "Chapter 1" in formatted

    def test_citation_without_page_number(self, service):
        chunk = make_chunk("c1", "text", page_number=None)
        chunk["metadata"].pop("page_number")
        citation = service._create_citation(chunk, 1)
        formatted = service.format_citation_text(citation, "apa")
        assert "Page" not in formatted


# ---------------------------------------------------------------------------
# T052-F: deduplicate_citations()
# ---------------------------------------------------------------------------

class TestDeduplicateCitations:
    @pytest.fixture
    def service(self):
        return CitationService()

    def test_no_duplicates_unchanged(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        deduped = service.deduplicate_citations(citations)
        assert len(deduped) == len(citations)

    def test_duplicates_removed(self, service):
        # Two citations with same chunk_id
        c1 = service._create_citation(SAMPLE_CHUNKS[0], 1)
        c2 = service._create_citation(SAMPLE_CHUNKS[0], 2)  # Same chunk_id
        deduped = service.deduplicate_citations([c1, c2])
        assert len(deduped) == 1

    def test_empty_list_returns_empty(self, service):
        assert service.deduplicate_citations([]) == []

    def test_order_preserved_after_dedup(self, service):
        citations = service.generate_citations(SAMPLE_CHUNKS)
        deduped = service.deduplicate_citations(citations)
        for orig, dedup in zip(citations, deduped):
            assert orig["chunk_id"] == dedup["chunk_id"]

    def test_citation_without_chunk_id_included_once(self, service):
        c_no_id = {"id": "cite-1", "number": 1, "text": "test", "source": {}}
        result = service.deduplicate_citations([c_no_id, c_no_id])
        # chunk_id is None → not tracked → both included
        assert len(result) == 2
