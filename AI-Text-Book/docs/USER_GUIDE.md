# User Guide — AI Textbook Chatbot

> **T137** — How to use the RAG-powered chatbot features.

## Overview

The Physical AI Textbook includes an AI-powered chatbot that answers questions using content exclusively from the textbook. It supports multiple modes and features to match your learning style.

---

## Getting Started

The chat panel appears as a button in the bottom-right corner of every textbook page. Click it to open the chat interface.

---

## Chat Modes

### 1. Book-Only Mode (Default)
Ask questions about textbook content. The AI answers using only what's in the book, with source citations for every claim.

**Best for**: Understanding concepts, reviewing material, exploring topics in depth.

**Example questions**:
- "What is a ROS2 node?"
- "Explain the difference between topics and services in ROS2"
- "How does Nav2 handle obstacle avoidance?"

---

### 2. Selected-Text Mode
Highlight any text on the page, then click "Ask AI about this" to ask questions about the selected passage.

**How to use**:
1. Select text by clicking and dragging
2. A popup menu appears with "Ask AI about this"
3. Click it — the chat opens with your selection as context
4. Type your question

**Best for**: Clarifying specific paragraphs, going deeper on a concept you're reading.

**Limits**: Selections must be 50–4,000 tokens (roughly 40–3,000 words).

---

### 3. General Knowledge Mode
Ask questions that combine textbook content with the AI's broader knowledge.

**Note**: Responses in this mode may include information not in the textbook. A disclaimer is shown.

**Best for**: Connecting textbook concepts to real-world applications.

---

## Response Tones

Use the tone selector to adjust the language style of responses:

| Tone | Description |
|------|-------------|
| **Neutral** | Balanced, clear explanations (default) |
| **Academic** | Technical terminology, formal citations |
| **Beginner-Friendly** | Simple language, analogies, examples |
| **Concise** | Short, direct answers |
| **Detailed** | Comprehensive, step-by-step explanations |

**Note**: Tone only affects language style. Citations and accuracy are never altered by tone selection.

---

## Key Term Highlighting

Domain-specific terms (ROS2, SLAM, URDF, etc.) are highlighted with a dashed underline throughout the textbook.

- **Hover** over a term to see its definition
- **Click "More about [term]"** to open a pre-filled chat question
- **Toggle highlighting** with the highlight button in the chat panel

---

## Citations

Every answer includes source citations with:
- Chapter and section name
- Page number (when available)
- Confidence score (0–1)
- Preview of the source text

Click a citation to jump to the source location in the textbook.

---

## Limitations

- The chatbot only knows what's in the textbook (Book-Only mode)
- It cannot browse the internet or access external resources
- Maximum question length: 500 characters
- If a question is outside the textbook content, the chatbot will say so

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Something went wrong" | Check your internet connection; refresh the page |
| "Rate limit exceeded" | Wait a moment before sending another message |
| No response / very slow | The AI is processing; long questions take longer |
| Incorrect answer | Check the cited sources; use Book-Only mode for accuracy |
| Chat panel not loading | Try refreshing the page (Ctrl+F5) |

---

*Last reviewed: 2026-02-28*
