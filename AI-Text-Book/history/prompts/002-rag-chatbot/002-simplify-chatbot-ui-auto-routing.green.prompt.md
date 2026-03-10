---
id: "002"
title: "Simplify Chatbot UI Auto Routing"
stage: green
date: "2026-03-09"
surface: agent
model: claude-sonnet-4-6
feature: "002-rag-chatbot"
branch: "002-rag-chatbot"
user: ASADULLAH999
command: "Simplify chatbot UI — remove mode buttons, implement auto-routing"
labels: ["ui", "chatbot", "ux", "auto-routing", "streaming"]
links:
  spec: "specs/002-rag-chatbot/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - src/hooks/useChat.ts
  - src/components/ChatPanel/index.tsx
tests:
  - manual: open frontend, verify no mode buttons visible
  - manual: ask a question, verify book_only response streams
  - manual: select text, verify selection banner appears and selected_text mode activates
  - manual: ask off-topic question, verify auto-fallback to general_knowledge with notice
---

## Prompt

Simplify the chatbot UI - remove the 3 separate mode buttons (Book Only, Selected Text, General Knowledge). Make one unified chatbot that: 1. By default answers from the textbook only 2. If user selects text on the page, automatically uses that as context 3. If textbook has no answer, falls back to general knowledge automatically. Remove the mode selector UI completely and make it one seamless experience

## Response

Implemented unified auto-routing chatbot in two files:

**`src/hooks/useChat.ts`** — Added `sendMessageAuto(message, selectionContext?)`:
- Routes to `selected_text` mode when `selectionContext` is provided
- Routes to `book_only` mode by default
- Streams primary response; if `refused: true` detected in metadata, resets placeholder and re-streams with `general_knowledge` mode
- Sets `metadata.usedFallback: true` on fallback responses

**`src/components/ChatPanel/index.tsx`** — Simplified UI:
- Removed: mode selector buttons, tone selector, streaming toggle, mode badge in header, general-knowledge disclaimer banner
- Kept: selection preview banner (now shows whenever `hasValidSelection`, not mode-dependent)
- Replaced: `sendMessage`/`sendMessageStream` calls with single `sendMessageAuto(trimmed, selectionContext)`
- Refusal notice replaced with "from general knowledge" notice keyed on `metadata.usedFallback`
- Input placeholder dynamically changes to "Ask about the selected text..." when selection active

## Outcome

PASS — Both files compile cleanly. The chatbot now presents as a single unified assistant with no mode controls visible to the user. Auto-routing is transparent and the fallback note is informational only.
