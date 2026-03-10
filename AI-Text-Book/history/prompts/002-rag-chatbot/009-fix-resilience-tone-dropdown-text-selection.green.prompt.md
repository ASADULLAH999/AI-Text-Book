---
id: "009"
title: Fix resilience syntax, add tone dropdown, wire TextSelection
stage: green
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: 002-rag-chatbot
branch: 002-rag-chatbot
user: user
command: "Fix all issues: resilience.py syntax error, tone dropdown, TextSelection wiring"
labels: ["bug-fix", "tone", "text-selection", "resilience", "chatpanel"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - api/src/services/resilience.py
  - src/hooks/useChat.ts
  - src/components/ChatPanel/index.tsx
  - src/theme/Root.tsx
tests: []
---

## Prompt

> Yes, fix all issues starting with resilience.py syntax error on line 73, then add tone dropdown to ChatPanel, then wire TextSelection to chat input

## Response

Applied three fixes in order:

**1. resilience.py syntax error (line 73)**
Changed invalid `raise except Exception as e:` to `raise` — Python syntax error that blocked the entire API module import.

**2. Tone dropdown in ChatPanel**
- Imported `useTone` hook and `Tone`/`TONE_CONFIGS` from existing types
- Added `const { currentTone, setTone } = useTone()` in ChatPanel
- Rendered tone `<select>` dropdown in header using existing `.toneSelectorWrapper` / `.toneSelectorSelect` CSS classes
- Switched from `sendMessage` to `sendMessageAuto` so all submits benefit from auto-routing + selection context
- Updated `useChat.ts`: added `tone?: string` to `sendMessageAuto` signature and passed it through to both primary and fallback requests

**3. Wire TextSelection → ChatPanel**
- `Root.tsx`: Added `useTextSelection` hook and `SelectionMenu` component; shared `pendingSelection` state passed as prop to ChatPanel; `handleAskAI` sets selection, `handleSelectionCleared` clears it
- `ChatPanel/index.tsx`: Accepts `pendingSelection?: string | null` and `onSelectionCleared?: () => void` props; auto-opens when a selection arrives; shows selection preview banner (`.selectionPreviewBanner` CSS) with truncated text and dismiss button; builds `SelectionContext` from pending selection before calling `sendMessageAuto`; updates textarea placeholder to contextual prompt when selection active

## Outcome

- API no longer blocked by syntax error
- Users can pick response tone (Neutral / Academic / Beginner-Friendly / Concise / Detailed) from dropdown in chat header, persisted across sessions
- Highlighting text in docs now shows floating "Ask AI about this" menu; clicking it opens ChatPanel with selection preview banner and routes query via `selected_text` mode
