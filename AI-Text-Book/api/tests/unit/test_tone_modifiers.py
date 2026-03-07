"""
Unit Tests — Tone Modifiers
T087 [US4] — Verify tone prompt modifiers are correct, complete, and tone-agnostic
with respect to citations.

Run with: pytest api/tests/unit/test_tone_modifiers.py -v
"""

import pytest
from services.prompts.tone_modifiers import (
    Tone,
    DEFAULT_TONE,
    VALID_TONES,
    apply_tone_to_system_prompt,
    get_tone_modifier,
    is_valid_tone,
)


# ---------------------------------------------------------------------------
# Tone enum completeness
# ---------------------------------------------------------------------------


class TestToneEnum:
    """Validate the Tone enum covers all required values."""

    def test_all_five_tones_present(self):
        tone_values = {t.value for t in Tone}
        required = {"neutral", "academic", "beginner_friendly", "concise", "detailed"}
        assert required == tone_values, f"Missing tones: {required - tone_values}"

    def test_default_tone_is_neutral(self):
        assert DEFAULT_TONE == Tone.NEUTRAL

    def test_valid_tones_set_matches_enum(self):
        assert VALID_TONES == {t.value for t in Tone}


# ---------------------------------------------------------------------------
# get_tone_modifier
# ---------------------------------------------------------------------------


class TestGetToneModifier:
    """Verify get_tone_modifier returns non-empty strings for all tones."""

    @pytest.mark.parametrize("tone", [t.value for t in Tone])
    def test_modifier_is_non_empty(self, tone):
        modifier = get_tone_modifier(tone)
        assert isinstance(modifier, str)
        assert len(modifier.strip()) > 0, f"Empty modifier for tone '{tone}'"

    def test_unknown_tone_falls_back_to_neutral(self):
        neutral_modifier = get_tone_modifier(Tone.NEUTRAL.value)
        fallback_modifier = get_tone_modifier("completely_unknown_tone")
        assert fallback_modifier == neutral_modifier

    def test_each_tone_has_distinct_modifier(self):
        """Each tone must produce a unique modifier string."""
        modifiers = [get_tone_modifier(t.value) for t in Tone]
        assert len(set(modifiers)) == len(Tone), "Two tones share an identical modifier"

    def test_academic_modifier_contains_formal_language_cue(self):
        modifier = get_tone_modifier(Tone.ACADEMIC.value)
        assert any(
            word in modifier.lower()
            for word in ("formal", "academic", "precise", "terminology")
        )

    def test_beginner_friendly_modifier_contains_simplicity_cue(self):
        modifier = get_tone_modifier(Tone.BEGINNER_FRIENDLY.value)
        assert any(
            word in modifier.lower()
            for word in ("plain", "simple", "beginner", "analogi", "accessible")
        )

    def test_concise_modifier_contains_brevity_cue(self):
        modifier = get_tone_modifier(Tone.CONCISE.value)
        assert any(
            word in modifier.lower()
            for word in ("brief", "concise", "short", "bullet")
        )

    def test_detailed_modifier_contains_comprehensiveness_cue(self):
        modifier = get_tone_modifier(Tone.DETAILED.value)
        assert any(
            word in modifier.lower()
            for word in ("comprehensive", "detail", "context", "thorough")
        )


# ---------------------------------------------------------------------------
# apply_tone_to_system_prompt
# ---------------------------------------------------------------------------


class TestApplyToneToSystemPrompt:
    """Verify that tone modifiers are correctly appended to system prompts."""

    BASE_PROMPT = "You are a textbook chatbot. Answer questions using only book content."

    def test_returns_string(self):
        result = apply_tone_to_system_prompt(self.BASE_PROMPT, Tone.NEUTRAL.value)
        assert isinstance(result, str)

    def test_base_prompt_preserved(self):
        """The original base prompt must be present in the combined output."""
        for tone in Tone:
            combined = apply_tone_to_system_prompt(self.BASE_PROMPT, tone.value)
            assert self.BASE_PROMPT in combined, (
                f"Base prompt lost for tone '{tone.value}'"
            )

    def test_modifier_appended(self):
        """Modifier text must appear after the base prompt."""
        for tone in Tone:
            modifier = get_tone_modifier(tone.value)
            combined = apply_tone_to_system_prompt(self.BASE_PROMPT, tone.value)
            base_pos = combined.index(self.BASE_PROMPT)
            modifier_pos = combined.index(modifier)
            assert modifier_pos > base_pos, (
                f"Modifier appears before base prompt for tone '{tone.value}'"
            )

    def test_unknown_tone_returns_base_prompt_extended(self):
        """Unknown tone falls back to neutral — base prompt still present."""
        combined = apply_tone_to_system_prompt(self.BASE_PROMPT, "nonexistent_tone")
        assert self.BASE_PROMPT in combined

    def test_citation_instructions_not_in_modifier(self):
        """
        T085 [US4] — Tone modifiers must not contain citation instructions,
        chunk IDs, or grounding rules that could interfere with citations.
        """
        forbidden_phrases = ("chunk_id", "citation", "hallucination", "grounding")
        for tone in Tone:
            modifier = get_tone_modifier(tone.value)
            for phrase in forbidden_phrases:
                assert phrase not in modifier.lower(), (
                    f"Tone modifier for '{tone.value}' contains forbidden phrase '{phrase}'"
                )


# ---------------------------------------------------------------------------
# is_valid_tone
# ---------------------------------------------------------------------------


class TestIsValidTone:
    """Validate the tone membership check."""

    @pytest.mark.parametrize("tone", [t.value for t in Tone])
    def test_all_valid_tones_accepted(self, tone):
        assert is_valid_tone(tone) is True

    def test_empty_string_rejected(self):
        assert is_valid_tone("") is False

    def test_unknown_string_rejected(self):
        assert is_valid_tone("sarcastic") is False

    def test_case_sensitive_rejection(self):
        assert is_valid_tone("ACADEMIC") is False
        assert is_valid_tone("Neutral") is False
