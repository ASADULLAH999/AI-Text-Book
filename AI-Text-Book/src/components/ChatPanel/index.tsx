/**
 * ChatPanel Component
 * Pure book-only RAG chatbot — answers strictly from textbook content.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useChat } from '../../hooks/useChat';
import { useTone } from '../../hooks/useTone';
import { Tone, TONE_CONFIGS } from '../../types/tone';
import { Mode } from '../../types/mode';
import type { SelectionContext } from '../../services/chatApi';
import CitationCard from '../Citation/CitationCard';
import type { ApiCitation } from '../../services/chatApi';
import styles from './styles.module.css';

const MAX_INPUT_CHARS = 2000;
const GREETING = "Hi! I am your Textbook Assistant. Ask me anything about the course!";

export interface ChatPanelProps {
  /** Selected text passed in from Root via SelectionMenu */
  pendingSelection?: string | null;
  /** Called when ChatPanel has consumed/dismissed the pending selection */
  onSelectionCleared?: () => void;
}

/**
 * ChatPanel — fixed floating chat assistant panel.
 */
export default function ChatPanel({
  pendingSelection,
  onSelectionCleared,
}: ChatPanelProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const messageListRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { currentTone, setTone } = useTone();

  const {
    messages,
    isLoading,
    isStreaming,
    error,
    sendMessageAuto,
    clearMessages,
    clearError,
  } = useChat(Mode.BOOK_ONLY);

  // Auto-open when a text selection arrives
  useEffect(() => {
    if (pendingSelection) {
      setIsOpen(true);
    }
  }, [pendingSelection]);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [inputValue]);

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      if (e) e.preventDefault();
      const trimmed = inputValue.trim();
      if (!trimmed || isLoading || isStreaming) return;
      setInputValue('');

      // Build selection context if text was highlighted
      const selectionCtx: SelectionContext | undefined = pendingSelection
        ? {
            selected_text: pendingSelection,
            token_count: Math.ceil(pendingSelection.length / 4),
          }
        : undefined;

      // Clear the pending selection before sending
      if (pendingSelection && onSelectionCleared) {
        onSelectionCleared();
      }

      await sendMessageAuto(trimmed, selectionCtx, currentTone);
    },
    [inputValue, isLoading, isStreaming, sendMessageAuto, pendingSelection, onSelectionCleared, currentTone]
  );

  /**
   * Submit on Enter (but allow Shift+Enter for newlines).
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  /**
   * Format a timestamp to HH:MM.
   */
  function formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  const charCount = inputValue.length;
  const charCountClass =
    charCount >= MAX_INPUT_CHARS
      ? styles.charCounterLimit
      : charCount >= MAX_INPUT_CHARS * 0.9
      ? styles.charCounterWarning
      : '';

  const busy = isLoading || isStreaming;

  // When closed: render small FAB only
  if (!isOpen) {
    return (
      <button
        className={styles.fab}
        onClick={() => setIsOpen(true)}
        aria-label="Open chat assistant"
        title="Ask the Textbook"
      >
        💬
      </button>
    );
  }

  return (
    <div
      className={styles.chatPanel}
      role="complementary"
      aria-label="AI Textbook Assistant"
    >
      {/* ── Header ────────────────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h2 className={styles.title}>
            <span className={styles.icon}>🤖</span>
            Ask the Textbook
          </h2>

          <div className={styles.headerActions}>
            {messages.length > 0 && (
              <button
                className={styles.clearButton}
                onClick={clearMessages}
                title="Clear conversation"
                aria-label="Clear conversation"
              >
                🗑️
              </button>
            )}
            <button
              className={styles.collapseButton}
              onClick={() => setIsOpen(false)}
              title="Close chat"
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>
        </div>

        {/* ── Tone selector ──────────────────────────────── */}
        <div className={styles.toneSelectorWrapper}>
          <label className={styles.toneSelectorLabel} htmlFor="tone-select">
            Tone:
          </label>
          <div className={styles.toneSelectorControl}>
            <select
              id="tone-select"
              className={styles.toneSelectorSelect}
              value={currentTone}
              onChange={(e) => setTone(e.target.value as Tone)}
              aria-label="Response tone"
            >
              {Object.values(Tone).map((tone) => {
                const cfg = TONE_CONFIGS[tone];
                return (
                  <option key={tone} value={tone}>
                    {cfg.icon} {cfg.label}
                  </option>
                );
              })}
            </select>
          </div>
          <span className={styles.toneSelectorDesc}>
            {TONE_CONFIGS[currentTone].description}
          </span>
        </div>
      </div>

      {/* ── Body ──────────────────────────────────────────── */}
      <div className={styles.content}>
          {/* Error banner */}
          {error && (
            <div className={styles.error} role="alert">
              <span>{error}</span>
              <button
                className={styles.errorClose}
                onClick={clearError}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          {/* Selection preview banner */}
          {pendingSelection && (
            <div className={styles.selectionPreviewBanner} role="status" aria-live="polite">
              <span className={styles.selectionPreviewLabel}>📌 Asking about:</span>
              <span className={styles.selectionPreviewText}>
                {pendingSelection.length > 120
                  ? pendingSelection.slice(0, 120) + '…'
                  : pendingSelection}
              </span>
              <button
                className={styles.selectionPreviewClear}
                onClick={onSelectionCleared}
                aria-label="Clear selected text"
                title="Remove selection context"
              >
                ×
              </button>
            </div>
          )}

          {/* Message list */}
          <div
            className={styles.messageList}
            ref={messageListRef}
            role="log"
            aria-live="polite"
            aria-label="Chat messages"
          >
            {/* Greeting — always shown as first item */}
            <div className={styles.assistantMessage}>
              <div className={styles.messageHeader}>
                <span className={styles.messageRole}>🤖 Assistant</span>
              </div>
              <div className={styles.messageContent}>{GREETING}</div>
            </div>

            {messages.length > 0 && (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`${styles.message} ${
                    msg.role === 'user' ? styles.userMessage : styles.assistantMessage
                  }`}
                >
                  <div className={styles.messageHeader}>
                    <span className={styles.messageRole}>
                      {msg.role === 'user' ? 'You' : '🤖 Assistant'}
                    </span>
                    <span className={styles.messageTime}>
                      {formatTime(msg.timestamp)}
                    </span>
                  </div>

                  <div className={styles.messageContent}>
                    {msg.content}
                    {msg.isStreaming && (
                      <span className={styles.streamingCursor} aria-hidden>
                        ▌
                      </span>
                    )}
                  </div>

                  {/* Error badge */}
                  {msg.metadata?.error && (
                    <span className={styles.errorBadge}>Error</span>
                  )}

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className={styles.citations}>
                      <div className={styles.citationsHeader}>
                        <span className={styles.citationsIcon}>📚</span>
                        Sources ({msg.citations.length})
                      </div>
                      <div className={styles.citationsList}>
                        {msg.citations.map((citation: ApiCitation, idx: number) => (
                          <CitationCard
                            key={`${msg.id}-cit-${idx}`}
                            citation={citation}
                            index={idx + 1}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}

            {/* Loading indicator */}
            {busy && !isStreaming && (
              <div className={styles.loadingIndicator} aria-label="Loading…">
                <div className={styles.loadingDots}>
                  <span />
                  <span />
                  <span />
                </div>
                Thinking…
              </div>
            )}
          </div>

          {/* ── Input form ────────────────────────────────── */}
          <form className={styles.chatInputForm} onSubmit={handleSubmit}>
            <div className={styles.inputContainer}>
              <textarea
                ref={textareaRef}
                className={styles.textarea}
                value={inputValue}
                onChange={(e) =>
                  setInputValue(e.target.value.slice(0, MAX_INPUT_CHARS))
                }
                onKeyDown={handleKeyDown}
                placeholder={
                  pendingSelection
                    ? 'Ask a question about the selected text…'
                    : 'Ask about the course content…'
                }
                disabled={busy}
                rows={1}
                aria-label="Chat input"
              />

              {/* Character counter */}
              {inputValue.length > MAX_INPUT_CHARS * 0.7 && (
                <span
                  className={`${styles.charCounter} ${charCountClass}`}
                  aria-live="polite"
                >
                  {charCount}/{MAX_INPUT_CHARS}
                </span>
              )}

              <button
                type="submit"
                className={styles.sendButton}
                disabled={!inputValue.trim() || busy}
                aria-label="Send message"
              >
                ➤
              </button>
            </div>

            <div className={styles.helperText}>
              <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for newline
            </div>
          </form>
        </div>
    </div>
  );
}
