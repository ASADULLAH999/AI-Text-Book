"""
Tone Prompt Modifiers
T084 [US4] — Defines per-tone system-prompt additions for response style.

Tone affects language style ONLY.
Citations, factual accuracy, and chunk retrieval are never altered by tone.
"""

from enum import Enum
from typing import Dict


class Tone(str, Enum):
    """Response tone enum — must match src/types/tone.ts on the frontend."""

    NEUTRAL = "neutral"
    ACADEMIC = "academic"
    BEGINNER_FRIENDLY = "beginner_friendly"
    CONCISE = "concise"
    DETAILED = "detailed"


# Default tone applied when none is specified
DEFAULT_TONE: Tone = Tone.NEUTRAL

# Mapping from tone value strings to Tone enum (for validation)
VALID_TONES: frozenset = frozenset(t.value for t in Tone)


# ---------------------------------------------------------------------------
# Per-tone system-prompt modifiers
# ---------------------------------------------------------------------------

_TONE_MODIFIERS: Dict[Tone, str] = {
    Tone.NEUTRAL: (
        "Respond in a clear, balanced manner. "
        "Use straightforward language without unnecessary jargon or over-simplification."
    ),
    Tone.ACADEMIC: (
        "Respond in a formal, academic register. "
        "Use precise discipline-specific terminology, structured argumentation, and "
        "reference evidence rigorously. Prefer passive constructions where appropriate "
        "and avoid colloquialisms."
    ),
    Tone.BEGINNER_FRIENDLY: (
        "Respond using plain, accessible language suitable for someone new to the topic. "
        "Break down complex ideas with everyday analogies and concrete examples. "
        "Avoid jargon; when technical terms are necessary, define them immediately. "
        "Use short sentences and a conversational, encouraging tone."
    ),
    Tone.CONCISE: (
        "Respond as briefly as possible while remaining accurate and complete. "
        "Use bullet points or very short paragraphs. "
        "Omit preamble, qualifications, and elaboration unless they are essential to "
        "understanding the answer."
    ),
    Tone.DETAILED: (
        "Respond comprehensively. "
        "Provide full context, relevant background, concrete examples, edge cases, "
        "and step-by-step explanations where appropriate. "
        "Structure the answer with clear headings or numbered sections for readability."
    ),
}

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_tone_modifier(tone: str) -> str:
    """
    Return the system-prompt modifier string for the requested tone.

    Args:
        tone: Tone value string (e.g. "academic"). Unknown values fall back to NEUTRAL.

    Returns:
        Modifier string to append to the system prompt.
    """
    try:
        tone_enum = Tone(tone)
    except ValueError:
        tone_enum = DEFAULT_TONE
    return _TONE_MODIFIERS[tone_enum]


def apply_tone_to_system_prompt(system_prompt: str, tone: str) -> str:
    """
    Append the tone modifier to an existing system prompt.

    Args:
        system_prompt: Base system prompt for the mode.
        tone: Tone value string.

    Returns:
        Combined system prompt with tone modifier appended.

    Note:
        This function NEVER modifies citation instructions or grounding rules
        embedded in the system prompt. It only appends style guidance.
    """
    modifier = get_tone_modifier(tone)
    if not modifier:
        return system_prompt
    return f"{system_prompt}\n\n# Response Style\n{modifier}"


def is_valid_tone(tone: str) -> bool:
    """Return True if *tone* is a recognised tone value."""
    return tone in VALID_TONES
