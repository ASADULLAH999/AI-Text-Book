---
id: 006
title: Implement Phase 6 Tone Customization T081-T088
stage: green
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: 002-rag-chatbot
branch: 002-rag-chatbot
user: architect
command: /sp.implement phase 6
labels: ["phase6","tone","us4","implementation","tests"]
links:
  spec: specs/002-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - api/src/services/prompts/__init__.py
  - api/src/services/prompts/tone_modifiers.py
  - api/src/services/citation_service.py
  - api/src/api/v1/chat.py
  - api/src/services/rag/orchestrator.py
  - api/tests/unit/test_tone_modifiers.py
  - api/tests/unit/test_citation_tone_consistency.py
  - src/services/chatApi.ts
  - specs/002-rag-chatbot/tasks.md
tests:
  - api/tests/unit/test_tone_modifiers.py (27 tests — PASS)
  - api/tests/unit/test_citation_tone_consistency.py (21 tests — PASS)
---

## Prompt

phase 6

(via /sp.implement)

## Response snapshot

Implemented all 8 Phase 6 tasks (T081–T088) for User Story 4 — Customize Response Tone:

- **T081–T083** (already complete): ToneSelector.tsx, tone.ts enum, useTone.ts hook
- **T084**: Created `api/src/services/prompts/tone_modifiers.py` with 5 tone modifiers (neutral, academic, beginner_friendly, concise, detailed), `get_tone_modifier()`, `apply_tone_to_system_prompt()`, and `is_valid_tone()` helpers
- **T085**: Added `validate_tone_isolation()` method to `CitationService` and tone-agnostic docstring; citations are structurally invariant to tone
- **T086**: Added optional `tone` field to `ChatRequest` Pydantic model in `chat.py`; validates against `VALID_TONES`; echoed in response metadata; wired into both `/chat` and `/chat/stream` endpoints; `sendChatMessage()` and `sendChatMessageStream()` helpers updated in `chatApi.ts`
- **T087**: Created `api/tests/unit/test_tone_modifiers.py` — 27 tests across 4 test classes covering enum completeness, per-tone modifier content, `apply_tone_to_system_prompt`, and `is_valid_tone`
- **T088**: Created `api/tests/unit/test_citation_tone_consistency.py` — 21 tests validating that 100-chunk citation output is structurally identical across all 5 tones

All 48 tests pass.

## Outcome

- ✅ Impact: Phase 6 fully implemented; tone parameter flows end-to-end (frontend → API → orchestrator metadata); citation integrity guaranteed across tones
- 🧪 Tests: 48 passed (27 tone_modifiers + 21 citation_tone_consistency), 0 failed
- 📁 Files: 9 files created/modified
- 🔁 Next prompts: /sp.implement phase 7 (Key Terms — T089–T097)
- 🧠 Reflection: T081–T083 were pre-existing; T084–T088 were the implementation gap. Tone is deliberately kept out of citation generation path to satisfy constitutional grounding requirements.

## Evaluation notes (flywheel)

- Failure modes observed: PYTHONPATH must include `api/src/` for tests to import `services.*` modules
- Graders run and results (PASS/FAIL): pytest 48/48 PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Wire tone into LLM system prompt when LLM integration is added to orchestrator
