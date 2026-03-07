/**
 * ChatPanel Component
 * T060–T086 [US2/US3/US4] — Floating RAG chatbot panel.
 *
 * Provides:
 *  - Mode selection (Book-Only / Selected-Text / General-Knowledge) [US3]
 *  - Tone selection [US4]
 *  - Text-selection preview and context passing [US2]
 *  - Streaming/non-streaming message exchange
 *  - Citation display per message
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useChat } from '../../hooks/useChat';
import { useTone } from '../../hooks/useTone';
import { useTextSelection } from '../../hooks/useTextSelection';
import { Mode, MODE_CONFIGS } from '../../types/mode';
import { Tone, TONE_CONFIGS } from '../../types/tone';
import CitationCard from '../Citation/CitationCard';
import type { ApiCitation } from '../../services/chatApi';
import styles from './styles.module.css';

/** Maximum character limit for the input textarea */
const MAX_INPUT_CHARS = 2000;

/** Color class per mode */
const MODE_COLOR: Record<Mode, string> = {
  [Mode.BOOK_ONLY]: styles.modeSelectorBtn_blue,
  [Mode.SELECTED_TEXT]: styles.modeSelectorBtn_purple,
  [Mode.GENERAL_KNOWLEDGE]: styles.modeSelectorBtn_amber,
};

const MODE_BADGE_COLOR: Record<Mode, string> = {
  [Mode.BOOK_ONLY]: styles.modeBadge_blue,
  [Mode.SELECTED_TEXT]: styles.modeBadge_purple,
  [Mode.GENERAL_KNOWLEDGE]: styles.modeBadge_amber,
};

/**
 * ChatPanel — fixed floating chat assistant panel.
 */
export default function ChatPanel(): JSX.Element {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [useStreaming, setUseStreaming] = useState(true);

  const messageListRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Core hooks
  const {
    messages,
    isLoading,
    isStreaming,
    error,
    currentMode,
    sendMessage,
    sendMessageStream,
    clearMessages,
    setMode,
    clearError,
  } = useChat(Mode.BOOK_ONLY);

  const { currentTone, setTone } = useTone();
  const { selection, clearSelection, hasValidSelection } = useTextSelection();

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

  /**
   * Handle form submission.
   */
  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      if (e) e.preventDefault();

      const trimmed = inputValue.trim();
      if (!trimmed || isLoading || isStreaming) return;

      setInputValue('');

      // Build filters: carry selected-text context in Selected-Text mode
      const filters =
        currentMode === Mode.SELECTED_TEXT && hasValidSelection && selection
          ? {
              selected_text: selection.text,
              token_count: selection.tokenCount,
            }
          : undefined;

      if (useStreaming) {
        await sendMessageStream(trimmed, currentMode, filters as any);
      } else {
        await sendMessage(trimmed, currentMode, filters as any);
      }

      // Clear selection after sending in Selected-Text mode
      if (currentMode === Mode.SELECTED_TEXT) {
        clearSelection();
      }
    },
    [
      inputValue,
      isLoading,
      isStreaming,
      currentMode,
      hasValidSelection,
      selection,
      useStreaming,
      sendMessageStream,
      sendMessage,
      clearSelection,
    ]
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

  return (
    <div
      className={`${styles.chatPanel}${isCollapsed ? ` ${styles.collapsed}` : ''}`}
      role="complementary"
      aria-label="AI Textbook Assistant"
    >
      {/* ── Header ────────────────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h2 className={styles.title}>
            <span className={styles.icon}>🤖</span>
            Ask the Textbook
            {/* Mode badge */}
            <span
              className={`${styles.modeBadge} ${MODE_BADGE_COLOR[currentMode]}`}
            >
              {MODE_CONFIGS[currentMode].icon} {MODE_CONFIGS[currentMode].label}
            </span>
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
              onClick={() => setIsCollapsed((prev) => !prev)}
              title={isCollapsed ? 'Expand' : 'Collapse'}
              aria-label={isCollapsed ? 'Expand chat' : 'Collapse chat'}
            >
              {isCollapsed ? '▲' : '▼'}
            </button>
          </div>
        </div>

        {/* Mode selector */}
        {!isCollapsed && (
          <>
            <div className={styles.modeSelectorButtons}>
              {Object.values(Mode).map((mode) => {
                const cfg = MODE_CONFIGS[mode];
                const isActive = currentMode === mode;
                return (
                  <button
                    key={mode}
                    className={[
                      styles.modeSelectorBtn,
                      MODE_COLOR[mode],
                      isActive ? styles.modeSelectorBtnActive : '',
                    ].join(' ')}
                    onClick={() => setMode(mode)}
                    disabled={busy}
                    title={cfg.description}
                    aria-pressed={isActive}
                  >
                    <span className={styles.modeSelectorIcon}>{cfg.icon}</span>
                    <span className={styles.modeSelectorLabel}>{cfg.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tone selector */}
            <div className={styles.toneSelectorWrapper}>
              <span className={styles.toneSelectorLabel}>Tone:</span>
              <div className={styles.toneSelectorControl}>
                <select
                  className={styles.toneSelectorSelect}
                  value={currentTone}
                  onChange={(e) => setTone(e.target.value as Tone)}
                  disabled={busy}
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
                <span className={styles.toneSelectorDesc}>
                  {TONE_CONFIGS[currentTone].description}
                </span>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ── Body (hidden when collapsed) ──────────────────── */}
      {!isCollapsed && (
        <div className={styles.content}>
          {/* General Knowledge disclaimer */}
          {currentMode === Mode.GENERAL_KNOWLEDGE && (
            <div className={styles.generalKnowledgeBanner} role="note">
              <span className={styles.generalKnowledgeBannerIcon}>⚠️</span>
              <span className={styles.generalKnowledgeBannerText}>
                General Knowledge mode may include information outside the textbook. Verify important facts independently.
              </span>
            </div>
          )}

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

          {/* Message list */}
          <div
            className={styles.messageList}
            ref={messageListRef}
            role="log"
            aria-live="polite"
            aria-label="Chat messages"
          >
            {messages.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>💬</div>
                <h4>Ask the textbook anything</h4>
                <p>
                  {currentMode === Mode.SELECTED_TEXT
                    ? 'Select text on the page, then ask a question about it.'
                    : "Type a question and I'll answer using the textbook content."}
                </p>
              </div>
            ) : (
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

                  {/* Refusal notice */}
                  {msg.refused && (
                    <div className={styles.refusalNotice}>
                      ⚠️ This question falls outside the textbook content. Switch to General Knowledge mode for broader answers.
                    </div>
                  )}

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
            {/* Selection preview */}
            {currentMode === Mode.SELECTED_TEXT && selection && (
              <div className={styles.selectionPreviewBanner}>
                <span className={styles.selectionPreviewLabel}>Selection:</span>
                <span className={styles.selectionPreviewText}>
                  {selection.text.slice(0, 80)}
                  {selection.text.length > 80 ? '…' : ''}
                </span>
                <button
                  type="button"
                  className={styles.selectionPreviewClear}
                  onClick={clearSelection}
                  aria-label="Clear selection"
                >
                  ×
                </button>
              </div>
            )}

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
                  currentMode === Mode.SELECTED_TEXT && !hasValidSelection
                    ? 'Select text on the page first…'
                    : 'Ask a question…'
                }
                disabled={
                  busy ||
                  (currentMode === Mode.SELECTED_TEXT && !hasValidSelection)
                }
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
                disabled={
                  !inputValue.trim() ||
                  busy ||
                  (currentMode === Mode.SELECTED_TEXT && !hasValidSelection)
                }
                aria-label="Send message"
              >
                ➤
              </button>
            </div>

            <div className={styles.helperText}>
              <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for newline ·{' '}
              <label style={{ cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={useStreaming}
                  onChange={(e) => setUseStreaming(e.target.checked)}
                  style={{ marginRight: 4 }}
                />
                Stream
              </label>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
