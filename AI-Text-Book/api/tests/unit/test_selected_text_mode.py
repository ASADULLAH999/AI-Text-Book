"""
Unit Tests — SelectedTextMode Service
T066 [P] [US2]

Tests cover:
- validate_selection(): boundary checks (empty, too short, too long, valid)
- build_context_chunk(): synthetic chunk structure
- create_refusal_response(): refusal message templates
- process_query(): end-to-end mode processing (no vector search)
- _estimate_tokens(): token estimation
- T068: Validate zero vector searches in Selected-Text mode
"""

import pytest
from services.modes.selected_text import SelectedTextMode, get_selected_text_mode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_selection_context(
    text: str = "Neural networks are computational models inspired by biological neurons. "
               "They use backpropagation to train on data and learn complex patterns.",
    token_count: int | None = None,
    chapter: str = "Chapter 1",
    section: str = "Introduction",
) -> dict:
    ctx = {
        "selected_text": text,
        "source_hint": {"chapter": chapter, "section": section},
    }
    if token_count is not None:
        ctx["token_count"] = token_count
    return ctx


VALID_SELECTION_TEXT = (
    "Neural networks are computational models inspired by biological neurons. "
    "Deep learning uses multiple stacked layers to extract hierarchical features. "
    "Backpropagation is the algorithm used to compute gradients. "
    "Activation functions like ReLU add non-linearity. "
    "Optimizers such as SGD update weights iteratively. " * 5
)  # ~250 tokens

TOO_SHORT_TEXT = "Short."  # < 50 tokens
TOO_LONG_TEXT = "word " * 4100  # > 4,000 tokens


# ---------------------------------------------------------------------------
# T066-A: SelectedTextMode instantiation
# ---------------------------------------------------------------------------

class TestSelectedTextModeInit:
    def test_default_parameters(self):
        svc = SelectedTextMode()
        assert svc.min_selection_tokens == 50
        assert svc.max_selection_tokens == 4000
        assert svc.chars_per_token == 4

    def test_custom_parameters(self):
        svc = SelectedTextMode(min_selection_tokens=20, max_selection_tokens=2000)
        assert svc.min_selection_tokens == 20
        assert svc.max_selection_tokens == 2000

    def test_min_chars_computed_correctly(self):
        svc = SelectedTextMode(min_selection_tokens=50, chars_per_token=4)
        assert svc.min_chars == 200

    def test_max_chars_computed_correctly(self):
        svc = SelectedTextMode(max_selection_tokens=4000, chars_per_token=4)
        assert svc.max_chars == 16000


# ---------------------------------------------------------------------------
# T066-B: validate_selection()
# ---------------------------------------------------------------------------

class TestValidateSelection:
    @pytest.fixture
    def svc(self):
        return SelectedTextMode()

    def test_empty_text_fails(self, svc):
        result = svc.validate_selection({"selected_text": ""})
        assert result["is_valid"] is False
        assert result["reason"] == "empty_selection"

    def test_whitespace_only_fails(self, svc):
        result = svc.validate_selection({"selected_text": "   \n\t  "})
        assert result["is_valid"] is False
        assert result["reason"] == "empty_selection"

    def test_too_short_fails(self, svc):
        result = svc.validate_selection({"selected_text": TOO_SHORT_TEXT})
        assert result["is_valid"] is False
        assert result["reason"] == "too_short"

    def test_too_long_fails(self, svc):
        result = svc.validate_selection({"selected_text": TOO_LONG_TEXT})
        assert result["is_valid"] is False
        assert result["reason"] == "too_long"

    def test_valid_selection_passes(self, svc):
        result = svc.validate_selection({"selected_text": VALID_SELECTION_TEXT})
        assert result["is_valid"] is True
        assert result["reason"] is None

    def test_client_token_count_used_when_provided(self, svc):
        # Client says 60 tokens — should be valid even if text is short
        result = svc.validate_selection({
            "selected_text": "Very short but client says 60 tokens.",
            "token_count": 60,
        })
        assert result["is_valid"] is True
        assert result["token_count"] == 60

    def test_client_token_count_too_short(self, svc):
        result = svc.validate_selection({
            "selected_text": "Some text",
            "token_count": 10,  # Client says 10 — below minimum
        })
        assert result["is_valid"] is False
        assert result["reason"] == "too_short"

    def test_client_token_count_too_long(self, svc):
        result = svc.validate_selection({
            "selected_text": "Some text",
            "token_count": 5000,  # Client says 5000 — above maximum
        })
        assert result["is_valid"] is False
        assert result["reason"] == "too_long"

    def test_token_count_returned_in_result(self, svc):
        result = svc.validate_selection({"selected_text": VALID_SELECTION_TEXT})
        assert "token_count" in result
        assert result["token_count"] > 0

    def test_boundary_at_exactly_50_tokens(self, svc):
        # Exactly at min: 50 tokens * 4 chars = 200 chars
        text = "a " * 100  # 200 chars ≈ 50 tokens
        result = svc.validate_selection({"selected_text": text, "token_count": 50})
        assert result["is_valid"] is True

    def test_boundary_at_exactly_4000_tokens(self, svc):
        result = svc.validate_selection({
            "selected_text": "some text",
            "token_count": 4000,
        })
        assert result["is_valid"] is True


# ---------------------------------------------------------------------------
# T066-C: build_context_chunk()
# ---------------------------------------------------------------------------

class TestBuildContextChunk:
    @pytest.fixture
    def svc(self):
        return SelectedTextMode()

    def test_chunk_structure(self, svc):
        ctx = make_selection_context(token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "score" in chunk
        assert "metadata" in chunk

    def test_chunk_id_is_selection_marker(self, svc):
        ctx = make_selection_context(token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["chunk_id"] == "selected_text_ctx"

    def test_chunk_text_matches_selection(self, svc):
        text = VALID_SELECTION_TEXT
        ctx = {"selected_text": text, "token_count": 100}
        chunk = svc.build_context_chunk(ctx)
        assert chunk["text"] == text

    def test_chunk_score_is_1(self, svc):
        ctx = make_selection_context(token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["score"] == 1.0

    def test_chunk_rerank_score_is_1(self, svc):
        ctx = make_selection_context(token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["rerank_score"] == 1.0

    def test_chunk_metadata_includes_chapter(self, svc):
        ctx = make_selection_context(chapter="Chapter 5", token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["metadata"]["chapter"] == "Chapter 5"

    def test_chunk_metadata_includes_section(self, svc):
        ctx = make_selection_context(section="Deep Learning", token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["metadata"]["section"] == "Deep Learning"

    def test_chunk_metadata_selection_mode_flag(self, svc):
        ctx = make_selection_context(token_count=100)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["metadata"]["selection_mode"] is True

    def test_chunk_metadata_token_count(self, svc):
        ctx = make_selection_context(token_count=150)
        chunk = svc.build_context_chunk(ctx)
        assert chunk["metadata"]["token_count"] == 150

    def test_chunk_without_source_hint_uses_defaults(self, svc):
        ctx = {"selected_text": VALID_SELECTION_TEXT, "token_count": 100}
        chunk = svc.build_context_chunk(ctx)
        assert chunk["metadata"]["chapter"] == "Selected Passage"
        assert chunk["metadata"]["section"] == "User Selection"


# ---------------------------------------------------------------------------
# T066-D: create_refusal_response()
# ---------------------------------------------------------------------------

class TestCreateRefusalResponse:
    @pytest.fixture
    def svc(self):
        return SelectedTextMode()

    def test_default_refusal_structure(self, svc):
        response = svc.create_refusal_response()
        assert "message" in response
        assert "refused" in response
        assert "citations" in response
        assert "metadata" in response

    def test_refused_flag_is_true(self, svc):
        response = svc.create_refusal_response()
        assert response["refused"] is True

    def test_citations_is_empty(self, svc):
        response = svc.create_refusal_response()
        assert response["citations"] == []

    def test_mode_in_metadata(self, svc):
        response = svc.create_refusal_response()
        assert response["metadata"]["mode"] == "selected_text"

    def test_vector_searches_zero_in_refusal(self, svc):
        response = svc.create_refusal_response()
        assert response["metadata"]["vector_searches_performed"] == 0

    def test_empty_selection_refusal_message(self, svc):
        response = svc.create_refusal_response("empty_selection")
        assert "selected" in response["message"].lower() or \
               "no text" in response["message"].lower()

    def test_insufficient_context_refusal_message(self, svc):
        response = svc.create_refusal_response("too_short")
        assert len(response["message"]) > 50  # Meaningful message

    def test_reason_recorded_in_metadata(self, svc):
        response = svc.create_refusal_response("too_long")
        assert response["metadata"]["refusal_reason"] == "too_long"


# ---------------------------------------------------------------------------
# T066-E: process_query() — T068 zero vector search invariant
# ---------------------------------------------------------------------------

class TestProcessQuery:
    @pytest.fixture
    def svc(self):
        return SelectedTextMode()

    def test_valid_selection_returns_not_refused(self, svc):
        ctx = make_selection_context(token_count=100)
        result = svc.process_query("What does this mean?", ctx)
        assert result["should_refuse"] is False

    def test_valid_selection_provides_context_chunks(self, svc):
        ctx = make_selection_context(token_count=100)
        result = svc.process_query("Explain this passage", ctx)
        assert len(result["context_chunks"]) == 1

    def test_invalid_selection_triggers_refusal(self, svc):
        ctx = {"selected_text": "Short."}
        result = svc.process_query("What is this?", ctx)
        assert result["should_refuse"] is True
        assert result["refusal_response"] is not None

    def test_empty_selection_triggers_refusal(self, svc):
        ctx = {"selected_text": ""}
        result = svc.process_query("Explain this", ctx)
        assert result["should_refuse"] is True

    # -----------------------------------------------------------------------
    # T068: Zero vector searches invariant
    # -----------------------------------------------------------------------

    def test_vector_searches_always_zero_on_valid_selection(self, svc):
        """T068: Selected-Text mode MUST perform zero vector searches."""
        ctx = make_selection_context(token_count=100)
        result = svc.process_query("What is neural network?", ctx)
        assert result["metadata"]["vector_searches_performed"] == 0

    def test_vector_searches_always_zero_on_refusal(self, svc):
        """T068: Even on refusal, vector searches remain zero."""
        ctx = {"selected_text": "Short."}
        result = svc.process_query("What?", ctx)
        assert result["metadata"]["vector_searches_performed"] == 0

    def test_vector_searches_zero_on_long_selection(self, svc):
        """T068: Over-long selections also perform no vector searches."""
        ctx = {"selected_text": TOO_LONG_TEXT}
        result = svc.process_query("Summarize this", ctx)
        assert result["metadata"]["vector_searches_performed"] == 0

    def test_context_chunk_has_correct_text(self, svc):
        text = VALID_SELECTION_TEXT
        ctx = {"selected_text": text, "token_count": 100}
        result = svc.process_query("What is backpropagation?", ctx)
        assert result["context_chunks"][0]["text"] == text

    def test_metadata_contains_selection_token_count(self, svc):
        ctx = make_selection_context(token_count=150)
        result = svc.process_query("Explain this", ctx)
        assert result["metadata"]["selection_token_count"] == 150

    def test_mode_in_metadata_is_selected_text(self, svc):
        ctx = make_selection_context(token_count=100)
        result = svc.process_query("What is this?", ctx)
        assert result["metadata"]["mode"] == "selected_text"


# ---------------------------------------------------------------------------
# T066-F: _estimate_tokens()
# ---------------------------------------------------------------------------

class TestEstimateTokens:
    @pytest.fixture
    def svc(self):
        return SelectedTextMode(chars_per_token=4)

    def test_empty_string_returns_one(self, svc):
        assert svc._estimate_tokens("") == 1

    def test_4_chars_equals_1_token(self, svc):
        assert svc._estimate_tokens("abcd") == 1

    def test_8_chars_equals_2_tokens(self, svc):
        assert svc._estimate_tokens("abcdefgh") == 2

    def test_long_text_approximation(self, svc):
        text = "a" * 400  # 400 chars / 4 = 100 tokens
        assert svc._estimate_tokens(text) == 100


# ---------------------------------------------------------------------------
# T066-G: Singleton factory
# ---------------------------------------------------------------------------

class TestGetSelectedTextMode:
    def test_returns_instance(self):
        svc = get_selected_text_mode()
        assert isinstance(svc, SelectedTextMode)

    def test_singleton_same_instance(self):
        svc1 = get_selected_text_mode()
        svc2 = get_selected_text_mode()
        assert svc1 is svc2

    def test_get_mode_info(self):
        svc = get_selected_text_mode()
        info = svc.get_mode_info()
        assert info["mode"] == "selected_text"
        assert info["vector_search"] is False
        assert info["color"] == "purple"
