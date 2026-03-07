/**
 * MessageList Component
 * Displays chat messages with scroll virtualization
 */

import React, { useEffect, useRef } from 'react';
import { ChatMessage } from '../../hooks/useChat';
import { ApiCitation } from '../../services/chatApi';
import CitationCard from '../Citation/CitationCard';
import styles from './styles.module.css';

export interface MessageListProps {
  /** List of messages to display */
  messages: ChatMessage[];
  /** Whether chat is currently loading */
  isLoading?: boolean;
  /** Citation click handler */
  onCitationClick?: (citation: ApiCitation) => void;
}

/**
 * MessageList - Scrollable list of chat messages
 */
export default function MessageList({
  messages,
  isLoading = false,
  onCitationClick,
}: MessageListProps): JSX.Element {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Scroll to bottom when new messages arrive
   */
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Format timestamp
   */
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div ref={containerRef} className={styles.messageList}>
      {messages.length === 0 && !isLoading && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>💬</div>
          <h4>Ask a question</h4>
          <p>Type your question below to get answers from the textbook with citations.</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`${styles.message} ${
            message.role === 'user' ? styles.userMessage : styles.assistantMessage
          }`}
        >
          <div className={styles.messageHeader}>
            <span className={styles.messageRole}>
              {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
            </span>
            <span className={styles.messageTime}>{formatTime(message.timestamp)}</span>
          </div>

          <div className={styles.messageContent}>
            {message.content}
            {message.isStreaming && <span className={styles.streamingCursor}>|</span>}
          </div>

          {/* Refusal notice */}
          {message.refused && (
            <div className={styles.refusalNotice}>
              <span>ℹ️ This response was limited to textbook content only.</span>
            </div>
          )}

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <div className={styles.citations}>
              <div className={styles.citationsHeader}>
                <span className={styles.citationsIcon}>📚</span>
                <span>Sources ({message.citations.length})</span>
              </div>
              <div className={styles.citationsList}>
                {message.citations.map((citation, index) => (
                  <CitationCard
                    key={citation.id}
                    citation={citation}
                    index={index + 1}
                    onClick={onCitationClick}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Metadata (for debugging) */}
          {message.metadata?.error && (
            <div className={styles.errorBadge}>
              <span>⚠️ Error occurred</span>
            </div>
          )}
        </div>
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className={styles.loadingIndicator}>
          <div className={styles.loadingDots}>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span>Thinking...</span>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
