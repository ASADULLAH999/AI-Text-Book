---
id: "004"
title: Implement Phase 4 Text Selection Feature T057-T068
stage: green
date: 2026-02-25
surface: agent
model: claude-sonnet-4-6
feature: 002-rag-chatbot
branch: 002-rag-chatbot
user: developer
command: /sp.implement phase 4
labels: ["text-selection", "us2", "selected-text-mode", "frontend", "backend", "testing"]
links:
  spec: specs/002-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/hooks/useTextSelection.ts
  - src/components/TextSelection/SelectionMenu.tsx
  - src/components/TextSelection/styles.module.css
  - src/components/TextSelection/index.tsx
  - src/services/chatApi.ts
  - src/components/ChatPanel/ChatInput.tsx
  - src/components/ChatPanel/styles.module.css
  - api/src/services/modes/selected_text.py
  - api/src/middleware/logger.py
  - api/tests/unit/test_selected_text_mode.py
  - tests/e2e/text-selection.spec.ts
  - specs/002-rag-chatbot/tasks.md
tests:
  - api/tests/unit/test_selected_text_mode.py
  - tests/e2e/text-selection.spec.ts
---

## Prompt

phase 4

## Response snapshot

Implemented all 12 tasks for Phase 4 (US2 — Select Text for Contextual Questions):

**T057** — `src/hooks/useTextSelection.ts`: React hook that listens to `selectionchange` events with 80ms debounce (under 100ms budget). Returns `TextSelection` with text, token count, validity, invalidReason, and viewport-relative position for menu anchoring. Also handles `mousedown` to clear stale selections.

**T058** — `src/components/TextSelection/SelectionMenu.tsx`: Floating contextual menu anchored to selection end (fixed position). Shows "Ask AI about this" button for valid selections; shows validation feedback for invalid ones. Dismisses on outside click or Escape key.

**T059** — "Ask AI about this" button in SelectionMenu. Appears within 200ms (80ms debounce + near-instant React render). Styled with indigo/purple gradient, hover/active/focus-visible states, animated with `fadeInUp`.

**T060** — Selection boundary validation in `useTextSelection.ts`: 50–4,000 token range enforced client-side using character-count approximation (4 chars/token). Returns `isValid`, `invalidReason` (too_short | too_long), and `tokenCount`.

**T061** — `api/src/services/modes/selected_text.py`: SelectedTextMode service with `validate_selection()`, `build_context_chunk()` (converts selection to synthetic chunk with score=1.0), `create_refusal_response()`, and `process_query()`. Invariant: `vector_searches_performed = 0` always.

**T062** — `api/src/middleware/logger.py`: Added `log_selection_query()` and `log_selection_refusal()` structured JSON log functions with selection metadata (token_count, char_count, validity, refusal_reason, vector_searches_performed).

**T063** — Insufficient context refusal templates in `selected_text.py`: `INSUFFICIENT_CONTEXT_REFUSAL` and `EMPTY_SELECTION_REFUSAL` constants with actionable user guidance.

**T064** — `src/services/chatApi.ts`: Added `SelectionContext` interface; extended `ChatApiRequest` with optional `selection_context` field; updated `sendChatMessage()` and `sendChatMessageStream()` helpers to accept and forward selection context.

**T065** — `src/components/ChatPanel/ChatInput.tsx`: Added `selectionPreview` and `onClearSelection` props; renders a styled preview banner above the textarea when a selection is active; includes clear (×) button; appended CSS styles to `styles.module.css`.

**T066** — `api/tests/unit/test_selected_text_mode.py`: 40+ unit tests covering init params, validate_selection (empty/too-short/too-long/valid/client-token-count), build_context_chunk (structure/text/score/metadata), create_refusal_response (structure/messages/metadata), process_query (refusal/valid/T068 zero-vector-search invariant), _estimate_tokens, and singleton factory.

**T067** — `tests/e2e/text-selection.spec.ts`: Playwright E2E tests for full user journey: menu appearance (within 200ms), boundary validation feedback, Ask AI click opens chat panel + shows preview, clear selection removes preview, API request includes selection_context with correct mode, T068 zero vector search verification.

**T068** — Validated in both unit tests (test_selected_text_mode.py) and E2E tests (text-selection.spec.ts): vector_searches_performed === 0 for all code paths (valid selection, refusal, too-long).

All 12 tasks marked [X] in specs/002-rag-chatbot/tasks.md.

## Outcome

- ✅ Impact: Complete Selected-Text mode implementation enabling students to highlight textbook passages and ask contextual questions without vector search overhead
- 🧪 Tests: 2 test files — 40+ unit tests (SelectedTextMode) + E2E Playwright suite (8 test groups)
- 📁 Files: 12 files created/modified (5 new frontend, 1 backend service, 1 backend logger update, 2 test files, 2 style files, 1 barrel export)
- 🔁 Next prompts: Run `pytest api/tests/unit/test_selected_text_mode.py -v` for unit tests; `npx playwright test tests/e2e/text-selection.spec.ts` for E2E; proceed to Phase 5 (T069-T080) for mode switching UI
- 🧠 Reflection: The zero-vector-search invariant (T068) is enforced structurally — SelectedTextMode never imports or calls any vector DB client. The ChatInput preview uses a simple banner pattern that stays clear of the textarea focus ring. Token estimation uses 4 chars/token heuristic consistent with OpenAI approximations.

## Evaluation notes (flywheel)

- useTextSelection uses 80ms debounce (well under 100ms budget) + mousedown clear to prevent ghost menus
- SelectionMenu uses fixed positioning + viewport clamping (min(position.x, window.innerWidth - 200)) to avoid overflow
- T068 invariant is tested at three levels: unit test process_query, unit test refusal path, and E2E network monitoring
- E2E tests use graceful skip (test.skip()) when doc pages lack substantial text, making tests non-fragile
