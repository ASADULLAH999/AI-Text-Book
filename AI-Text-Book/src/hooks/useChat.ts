/**
 * useChat Hook
 * Manages chat state and API interactions.
 *
 * T070 [US3] — Mode persisted in sessionStorage (clears on tab close).
 * T075 [US3] — Mode resets to Book-Only on new browser session.
 */

import { useState, useCallback, useRef } from 'react';
import {
  chatApi,
  ChatApiRequest,
  ChatApiResponse,
  ApiCitation,
} from '../services/chatApi';
import { Mode } from '../types/mode';

// ---------------------------------------------------------------------------
// T070 [US3] — sessionStorage key for mode persistence
// ---------------------------------------------------------------------------

const SESSION_STORAGE_MODE_KEY = 'chatbot_mode';

/**
 * Read mode from sessionStorage.
 * Falls back to BOOK_ONLY (T075 — default on new session).
 */
function readModeFromSession(): Mode {
  try {
    const stored = sessionStorage.getItem(SESSION_STORAGE_MODE_KEY);
    if (stored && Object.values(Mode).includes(stored as Mode)) {
      return stored as Mode;
    }
  } catch {
    // sessionStorage unavailable (SSR / private browsing edge cases)
  }
  return Mode.BOOK_ONLY;
}

/**
 * Persist mode to sessionStorage.
 */
function writeModeToSession(mode: Mode): void {
  try {
    sessionStorage.setItem(SESSION_STORAGE_MODE_KEY, mode);
  } catch {
    // Ignore write failures
  }
}

/**
 * Chat message interface
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: ApiCitation[];
  metadata?: any;
  isStreaming?: boolean;
  refused?: boolean;
}

/**
 * Chat state interface
 */
export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  currentMode: Mode;
}

/**
 * useChat hook return type
 */
export interface UseChatReturn {
  // State
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  currentMode: Mode;

  // Actions
  sendMessage: (message: string, mode?: Mode, filters?: ChatApiRequest['filters']) => Promise<void>;
  sendMessageStream: (message: string, mode?: Mode, filters?: ChatApiRequest['filters']) => Promise<void>;
  clearMessages: () => void;
  setMode: (mode: Mode) => void;
  clearError: () => void;
}

/**
 * useChat hook
 *
 * @param initialMode - Initial chat mode (overridden by sessionStorage if available)
 * @returns Chat state and actions
 */
export function useChat(initialMode: Mode = Mode.BOOK_ONLY): UseChatReturn {
  // T070 [US3] — Initialise from sessionStorage; default = BOOK_ONLY (T075)
  const resolvedInitialMode = readModeFromSession() || initialMode;

  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    isStreaming: false,
    error: null,
    currentMode: resolvedInitialMode,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Add a message to the chat
   */
  const addMessage = useCallback((message: ChatMessage) => {
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  }, []);

  /**
   * Update the last message
   */
  const updateLastMessage = useCallback((update: Partial<ChatMessage>) => {
    setState((prev) => {
      const messages = [...prev.messages];
      const lastIndex = messages.length - 1;
      if (lastIndex >= 0) {
        messages[lastIndex] = { ...messages[lastIndex], ...update };
      }
      return { ...prev, messages };
    });
  }, []);

  /**
   * Send a chat message (non-streaming)
   */
  const sendMessage = useCallback(
    async (
      message: string,
      mode: Mode = state.currentMode,
      filters?: ChatApiRequest['filters']
    ) => {
      // Abort any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Add user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // Set loading state
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        // Send API request
        const response: ChatApiResponse = await chatApi.sendMessage({
          message,
          mode,
          filters,
        });

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          timestamp: new Date(response.timestamp),
          citations: response.citations,
          metadata: response.metadata,
          refused: response.refused,
        };
        addMessage(assistantMessage);

        setState((prev) => ({ ...prev, isLoading: false }));
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'An unknown error occurred';

        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));

        // Add error message
        const errorMsg: ChatMessage = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}`,
          timestamp: new Date(),
          metadata: { error: true },
        };
        addMessage(errorMsg);
      }
    },
    [state.currentMode, addMessage]
  );

  /**
   * Send a chat message with streaming response
   */
  const sendMessageStream = useCallback(
    async (
      message: string,
      mode: Mode = state.currentMode,
      filters?: ChatApiRequest['filters']
    ) => {
      // Abort any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Add user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // Add placeholder assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      addMessage(assistantMessage);

      // Set streaming state
      setState((prev) => ({ ...prev, isStreaming: true, error: null }));

      try {
        let fullContent = '';
        let citations: ApiCitation[] = [];
        let metadata: any = {};

        // Stream response
        for await (const event of chatApi.sendMessageStream({
          message,
          mode,
          filters,
        })) {
          if (event.data) {
            const { type, content, citations: eventCitations, metadata: eventMetadata } = event.data;

            if (type === 'message_chunk' && content) {
              fullContent += content;
              updateLastMessage({ content: fullContent });
            } else if (type === 'citations' && eventCitations) {
              citations = eventCitations;
              updateLastMessage({ citations });
            } else if (type === 'metadata' && eventMetadata) {
              metadata = eventMetadata;
              updateLastMessage({ metadata });
            }
          }

          // Check for completion or error
          if (event.event === 'done') {
            updateLastMessage({ isStreaming: false });
            break;
          } else if (event.event === 'error') {
            throw new Error(event.data.error || 'Streaming error occurred');
          }
        }

        setState((prev) => ({ ...prev, isStreaming: false }));
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'An unknown error occurred';

        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: errorMessage,
        }));

        updateLastMessage({
          content: `Sorry, I encountered an error: ${errorMessage}`,
          isStreaming: false,
          metadata: { error: true },
        });
      }
    },
    [state.currentMode, addMessage, updateLastMessage]
  );

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setState((prev) => ({ ...prev, messages: [] }));
  }, []);

  /**
   * Set chat mode — T070 [US3] persists to sessionStorage
   */
  const setMode = useCallback((mode: Mode) => {
    writeModeToSession(mode);
    setState((prev) => ({ ...prev, currentMode: mode }));
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    isStreaming: state.isStreaming,
    error: state.error,
    currentMode: state.currentMode,
    sendMessage,
    sendMessageStream,
    clearMessages,
    setMode,
    clearError,
  };
}
