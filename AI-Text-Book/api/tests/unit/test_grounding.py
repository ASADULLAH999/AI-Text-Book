"""
Unit Tests — GroundingService
T051 [P] [US1]

Tests cover:
- validate_grounding(): grounding ratio calculation
- detect_hallucination(): risk scoring
- _is_grounded(): sentence-level grounding check
- _detect_uncited_facts(): fact pattern detection
- _calculate_hallucination_risk(): risk formula
"""

import pytest
from services.rag.grounding import GroundingService


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

def make_chunk(text: str, chunk_id: str = "c1") -> dict:
    return {"chunk_id": chunk_id, "text": text, "score": 0.9}


def make_citation(text: str, chunk_id: str = "c1") -> dict:
    return {
        "id": f"cite-1",
        "number": 1,
        "chunk_id": chunk_id,
        "text": text,
        "source": {"chapter": "Chapter 1", "section": "Intro"},
    }


CONTEXT_TEXT = (
    "Neural networks are computational models inspired by biological neurons. "
    "Deep learning uses multiple layers to extract hierarchical representations. "
    "Backpropagation is the algorithm used to train neural networks by computing gradients. "
    "Activation functions like ReLU introduce non-linearity into the network. "
    "Stochastic gradient descent is a common optimizer for training deep networks."
)

GROUNDED_RESPONSE = (
    "Neural networks are inspired by biological neurons. "
    "Deep learning uses multiple layers. "
    "Backpropagation computes gradients for training."
)

UNGROUNDED_RESPONSE = (
    "Quantum computing surpasses classical computing exponentially. "
    "The latest iPhone model uses a special chip. "
    "Mars colonization will begin in 2025 according to research shows."
)


# ---------------------------------------------------------------------------
# T051-A: GroundingService instantiation
# ---------------------------------------------------------------------------

class TestGroundingServiceInit:
    def test_default_parameters(self):
        svc = GroundingService()
        assert svc.min_overlap_ratio == 0.3
        assert svc.min_citation_coverage == 0.7

    def test_custom_parameters(self):
        svc = GroundingService(min_overlap_ratio=0.5, min_citation_coverage=0.8)
        assert svc.min_overlap_ratio == 0.5
        assert svc.min_citation_coverage == 0.8


# ---------------------------------------------------------------------------
# T051-B: validate_grounding()
# ---------------------------------------------------------------------------

class TestValidateGrounding:
    @pytest.fixture
    def service(self):
        return GroundingService(min_overlap_ratio=0.3)

    def test_grounded_response_passes(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        result = service.validate_grounding(GROUNDED_RESPONSE, chunks)
        assert result["is_grounded"] is True
        assert result["grounding_ratio"] > 0.3

    def test_ungrounded_response_fails(self, service):
        chunks = [make_chunk("Completely unrelated text about cooking recipes.")]
        result = service.validate_grounding(UNGROUNDED_RESPONSE, chunks)
        assert result["is_grounded"] is False

    def test_result_structure(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        result = service.validate_grounding(GROUNDED_RESPONSE, chunks)
        assert "is_grounded" in result
        assert "grounding_ratio" in result
        assert "grounded_sentences" in result
        assert "total_sentences" in result
        assert "ungrounded_sentences" in result

    def test_grounding_ratio_between_0_and_1(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        result = service.validate_grounding(GROUNDED_RESPONSE, chunks)
        assert 0.0 <= result["grounding_ratio"] <= 1.0

    def test_empty_response(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        result = service.validate_grounding("", chunks)
        assert result["grounding_ratio"] == 0.0
        assert result["total_sentences"] == 0

    def test_empty_chunks(self, service):
        result = service.validate_grounding(GROUNDED_RESPONSE, [])
        # No context → nothing is grounded
        assert result["grounding_ratio"] == 0.0

    def test_multiple_chunks_combined(self, service):
        chunks = [
            make_chunk("Neural networks use backpropagation.", "c1"),
            make_chunk("Deep learning extracts hierarchical features.", "c2"),
        ]
        response = "Neural networks use backpropagation and deep learning techniques."
        result = service.validate_grounding(response, chunks)
        assert result["is_grounded"] is True

    def test_ungrounded_sentences_are_sampled(self, service):
        chunks = [make_chunk("Short context only.")]
        result = service.validate_grounding(UNGROUNDED_RESPONSE, chunks)
        assert len(result["ungrounded_sentences"]) <= 3


# ---------------------------------------------------------------------------
# T051-C: detect_hallucination()
# ---------------------------------------------------------------------------

class TestDetectHallucination:
    @pytest.fixture
    def service(self):
        return GroundingService()

    def test_result_structure(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        citations = [make_citation(CONTEXT_TEXT[:100])]
        result = service.detect_hallucination(GROUNDED_RESPONSE, chunks, citations)
        assert "hallucination_risk" in result
        assert "grounding_ratio" in result
        assert "citation_coverage" in result
        assert "uncited_facts" in result
        assert "is_safe" in result

    def test_grounded_response_is_safe(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        citations = [make_citation("Neural networks are inspired by biological neurons.")]
        result = service.detect_hallucination(GROUNDED_RESPONSE, chunks, citations)
        assert result["hallucination_risk"] < 0.9
        assert isinstance(result["is_safe"], bool)

    def test_hallucination_risk_between_0_and_1(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        citations = []
        result = service.detect_hallucination(GROUNDED_RESPONSE, chunks, citations)
        assert 0.0 <= result["hallucination_risk"] <= 1.0

    def test_no_citations_increases_risk(self, service):
        chunks = [make_chunk(CONTEXT_TEXT)]
        result_no_citations = service.detect_hallucination(GROUNDED_RESPONSE, chunks, [])
        result_with_citations = service.detect_hallucination(
            GROUNDED_RESPONSE,
            chunks,
            [make_citation(CONTEXT_TEXT[:150])],
        )
        assert result_no_citations["hallucination_risk"] >= result_with_citations["hallucination_risk"]

    def test_uncited_facts_detected(self, service):
        response_with_facts = (
            "Studies indicate that neural networks achieve 95% accuracy. "
            "According to research, 2024 saw major breakthroughs."
        )
        chunks = [make_chunk("Some context")]
        result = service.detect_hallucination(response_with_facts, chunks, [])
        # Should detect the fact-bearing sentences
        assert len(result["uncited_facts"]) > 0


# ---------------------------------------------------------------------------
# T051-D: _is_grounded() (private — tested via validate_grounding)
# ---------------------------------------------------------------------------

class TestIsGrounded:
    @pytest.fixture
    def service(self):
        return GroundingService()

    def test_sentence_with_matching_words_is_grounded(self, service):
        sentence = "neural networks use backpropagation gradients"
        context = "neural networks use backpropagation to compute gradients"
        assert service._is_grounded(sentence, context) is True

    def test_sentence_with_no_match_is_ungrounded(self, service):
        sentence = "quantum computers solve NP-complete problems"
        context = "neural networks use backpropagation"
        assert service._is_grounded(sentence, context) is False

    def test_empty_sentence_is_grounded(self, service):
        # Trivial/empty sentence → True
        assert service._is_grounded("", "any context") is True

    def test_short_word_sentence_is_grounded(self, service):
        # All words ≤ 3 chars → True (trivial)
        assert service._is_grounded("a to in", "totally different context") is True


# ---------------------------------------------------------------------------
# T051-E: _calculate_hallucination_risk()
# ---------------------------------------------------------------------------

class TestCalculateHallucinationRisk:
    @pytest.fixture
    def service(self):
        return GroundingService()

    def test_perfect_grounding_low_risk(self, service):
        risk = service._calculate_hallucination_risk(1.0, 1.0, 0)
        assert risk < 0.1

    def test_zero_grounding_high_risk(self, service):
        risk = service._calculate_hallucination_risk(0.0, 0.0, 5)
        assert risk > 0.7

    def test_risk_between_0_and_1(self, service):
        for grounding, coverage, facts in [
            (0.0, 0.0, 0), (0.5, 0.5, 2), (1.0, 1.0, 0), (0.3, 0.7, 10)
        ]:
            risk = service._calculate_hallucination_risk(grounding, coverage, facts)
            assert 0.0 <= risk <= 1.0, f"Risk out of range: {risk}"

    def test_more_uncited_facts_increases_risk(self, service):
        risk_low = service._calculate_hallucination_risk(0.8, 0.8, 0)
        risk_high = service._calculate_hallucination_risk(0.8, 0.8, 5)
        assert risk_high > risk_low
