/**
 * ChatInput Component
 * Text input for chat messages with character limit
 */

import React, { useState, useRef, useEffect } from 'react';
import styles from './styles.module.css';

export interface ChatInputProps {
  /** Callback when message is sent */
  onSendMessage: (message: string) => void;
  /** Whether input is disabled */
  disabled?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Maximum character limit */
  maxLength?: number;
  /**
   * T065 [US2] — Selected text to show as a preview above the input.
   * When set, the user is in Selected-Text mode for this query.
   */
  selectionPreview?: string;
  /** T065 [US2] — Callback to clear the active selection context */
  onClearSelection?: () => void;
}

/**
 * ChatInput - Input field for chat messages
 */
export default function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your question...',
  maxLength = 500,
  selectionPreview,
  onClearSelection,
}: ChatInputProps): JSX.Element {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-resize textarea based on content
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  /**
   * Handle message submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    // Enforce character limit
    if (newValue.length <= maxLength) {
      setMessage(newValue);
    }
  };

  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 50;
  const isAtLimit = remainingChars === 0;

  return (
    <form onSubmit={handleSubmit} className={styles.chatInputForm}>
      {/* T065 [US2] — Selection preview banner */}
      {selectionPreview && (
        <div className={styles.selectionPreviewBanner} data-testid="selection-preview">
          <span className={styles.selectionPreviewLabel}>Selected:</span>
          <span className={styles.selectionPreviewText}>
            {selectionPreview.length > 120
              ? `${selectionPreview.slice(0, 120)}…`
              : selectionPreview}
          </span>
          {onClearSelection && (
            <button
              type="button"
              className={styles.selectionPreviewClear}
              onClick={onClearSelection}
              aria-label="Clear selected text context"
              title="Clear selection"
            >
              ×
            </button>
          )}
        </div>
      )}
      <div className={styles.inputContainer}>
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={styles.textarea}
          rows={1}
          maxLength={maxLength}
        />

        {/* Character counter */}
        {message.length > 0 && (
          <div
            className={`${styles.charCounter} ${
              isNearLimit ? styles.charCounterWarning : ''
            } ${isAtLimit ? styles.charCounterLimit : ''}`}
          >
            {remainingChars}
          </div>
        )}

        {/* Send button */}
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className={styles.sendButton}
          title="Send message (Enter)"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M2 10l16-8-8 16-2-8-6-0z" />
          </svg>
        </button>
      </div>

      {/* Helper text */}
      <div className={styles.helperText}>
        <span>Press <kbd>Enter</kbd> to send, <kbd>Shift+Enter</kbd> for new line</span>
      </div>
    </form>
  );
}
