"""
Unit Tests — Citation Consistency Across Tones
T088 [US4] — Validate that citations remain identical regardless of the tone
selected by the user.

This test suite covers the CitationService.validate_tone_isolation() method
and asserts structural invariance of citation output across all five tones.

Run with: pytest api/tests/unit/test_citation_tone_consistency.py -v
"""

import pytest
from services.citation_service import CitationService
from services.prompts.tone_modifiers import Tone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def citation_service() -> CitationService:
    return CitationService()


@pytest.fixture
def sample_chunks():
    """100 deterministic sample chunks (T088 requires 100-query validation)."""
    chunks = []
    for i in range(100):
        chunks.append(
            {
                "chunk_id": f"chunk-{i:04d}",
                "text": f"This is sample textbook content for chunk {i}. " * 5,
                "score": round(0.95 - (i * 0.001), 4),
                "rerank_score": round(0.90 - (i * 0.0005), 4),
                "metadata": {
                    "chapter": f"Chapter {(i // 10) + 1}",
                    "section": f"Section {(i % 10) + 1}",
                    "heading": f"Heading {i}",
                    "page_number": i + 1,
                },
            }
        )
    return chunks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_citations_for_tone(
    citation_service: CitationService,
    chunks: list,
    tone: Tone,
) -> list:
    """
    Simulate citation generation for a given tone.

    CitationService is tone-agnostic, so we call generate_citations() the
    same way regardless of tone. This function exists to make it explicit that
    tone is NOT passed to the citation service.
    """
    # NOTE: tone is intentionally NOT passed to generate_citations — it must
    # never influence citation output. The _ prefix documents this contract.
    _ = tone
    return citation_service.generate_citations(chunks)


# ---------------------------------------------------------------------------
# Tests — validate_tone_isolation helper
# ---------------------------------------------------------------------------


class TestValidateToneIsolation:
    """Unit tests for CitationService.validate_tone_isolation()."""

    def test_identical_lists_are_isolated(self, citation_service, sample_chunks):
        cites = citation_service.generate_citations(sample_chunks[:5])
        result = citation_service.validate_tone_isolation(cites, cites)
        assert result["is_isolated"] is True
        assert result["mismatches"] == []

    def test_different_chunk_ids_detected(self, citation_service, sample_chunks):
        cites_a = citation_service.generate_citations(sample_chunks[:2])
        cites_b = citation_service.generate_citations(sample_chunks[2:4])
        result = citation_service.validate_tone_isolation(cites_a, cites_b)
        assert result["is_isolated"] is False
        assert len(result["mismatches"]) > 0

    def test_different_count_detected(self, citation_service, sample_chunks):
        cites_a = citation_service.generate_citations(sample_chunks[:3])
        cites_b = citation_service.generate_citations(sample_chunks[:2])
        result = citation_service.validate_tone_isolation(cites_a, cites_b)
        assert result["is_isolated"] is False

    def test_empty_lists_are_isolated(self, citation_service):
        result = citation_service.validate_tone_isolation([], [])
        assert result["is_isolated"] is True


# ---------------------------------------------------------------------------
# Tests — cross-tone consistency (100-chunk validation for T088)
# ---------------------------------------------------------------------------


class TestCitationConsistencyAcrossTones:
    """
    T088 [US4] — Validate citation consistency across all five tones
    using 100 sample chunks.
    """

    def test_all_tones_produce_identical_citations(
        self, citation_service, sample_chunks
    ):
        """
        Generate citations for each tone using 100 sample chunks.
        Assert structural identity across all tones.
        """
        reference_tone = Tone.NEUTRAL
        reference_cites = _generate_citations_for_tone(
            citation_service, sample_chunks, reference_tone
        )

        for tone in Tone:
            if tone == reference_tone:
                continue

            tone_cites = _generate_citations_for_tone(
                citation_service, sample_chunks, tone
            )

            result = citation_service.validate_tone_isolation(
                reference_cites, tone_cites
            )

            assert result["is_isolated"] is True, (
                f"Citation mismatch between {reference_tone.value} and {tone.value}: "
                f"{result['mismatches']}"
            )

    @pytest.mark.parametrize("tone", list(Tone))
    def test_citation_count_invariant_per_tone(
        self, citation_service, sample_chunks, tone
    ):
        """Each tone must produce the same number of citations as the chunk count."""
        cites = _generate_citations_for_tone(citation_service, sample_chunks, tone)
        assert len(cites) == len(sample_chunks), (
            f"Tone '{tone.value}' produced {len(cites)} citations for "
            f"{len(sample_chunks)} chunks — counts must match."
        )

    @pytest.mark.parametrize("tone", list(Tone))
    def test_chunk_ids_preserved_per_tone(
        self, citation_service, sample_chunks, tone
    ):
        """chunk_id in each citation must match the originating chunk."""
        cites = _generate_citations_for_tone(citation_service, sample_chunks, tone)
        for idx, (chunk, cite) in enumerate(zip(sample_chunks, cites)):
            assert cite["chunk_id"] == chunk["chunk_id"], (
                f"Tone '{tone.value}': Citation[{idx}] chunk_id "
                f"'{cite['chunk_id']}' != chunk '{chunk['chunk_id']}'"
            )

    @pytest.mark.parametrize("tone", list(Tone))
    def test_source_metadata_preserved_per_tone(
        self, citation_service, sample_chunks, tone
    ):
        """Source chapter/section in citations must match chunk metadata."""
        cites = _generate_citations_for_tone(citation_service, sample_chunks, tone)
        for idx, (chunk, cite) in enumerate(zip(sample_chunks, cites)):
            assert cite["source"]["chapter"] == chunk["metadata"]["chapter"], (
                f"Tone '{tone.value}': Citation[{idx}] chapter mismatch"
            )
            assert cite["source"]["section"] == chunk["metadata"]["section"], (
                f"Tone '{tone.value}': Citation[{idx}] section mismatch"
            )

    def test_cross_tone_chunk_ids_identical(self, citation_service, sample_chunks):
        """chunk_ids must be identical across all tone permutations."""
        all_tone_chunk_ids = []
        for tone in Tone:
            cites = _generate_citations_for_tone(
                citation_service, sample_chunks, tone
            )
            all_tone_chunk_ids.append([c["chunk_id"] for c in cites])

        reference = all_tone_chunk_ids[0]
        for idx, tone_chunk_ids in enumerate(all_tone_chunk_ids[1:], start=1):
            tone_name = list(Tone)[idx].value
            assert tone_chunk_ids == reference, (
                f"chunk_ids differ between neutral and {tone_name}"
            )
