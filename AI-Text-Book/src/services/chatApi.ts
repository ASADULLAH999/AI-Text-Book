/**
 * Chat API Client
 * Handles communication with the RAG chatbot backend API
 */

import { Mode } from '../types/mode';

// API configuration
const API_BASE_URL = 'https://ai-text-book-production-54ed.up.railway.app';
const API_TIMEOUT = 30000;

/**
 * Selection context for Selected-Text mode.
 * T064 [US2] — Carries the highlighted passage to the backend.
 */
export interface SelectionContext {
  /** The exact text the user highlighted */
  selected_text: string;
  /** Approximate token count (estimated client-side) */
  token_count: number;
  /** Source location hints (optional) */
  source_hint?: {
    chapter?: string;
    section?: string;
  };
}

/**
 * Chat API request interface (matches backend)
 */
export interface ChatApiRequest {
  message: string;
  mode?: string;
  /** T086 [US4] — Response tone. Affects language style only, never citations. */
  tone?: string;
  filters?: {
    chapter?: string;
    section?: string;
    heading?: string;
    page_number?: number;
  };
  conversation_id?: string;
  /** T064 [US2] — Present when mode === 'selected_text' */
  selection_context?: SelectionContext;
}

/**
 * Citation from API
 */
export interface ApiCitation {
  id: string;
  number: number;
  chunk_id: string;
  text: string;
  score: number;
  source: {
    chapter: string;
    section: string;
    heading?: string;
    page_number?: number;
  };
  preview: string;
}

/**
 * Chat API response interface (matches backend)
 */
export interface ChatApiResponse {
  message: string;
  citations: ApiCitation[];
  refused: boolean;
  metadata: {
    mode: string;
    query?: string;
    retrieved_chunks?: number;
    timestamp?: string;
    error?: boolean;
    [key: string]: any;
  };
  timestamp: string;
}

/**
 * API error response
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp: string;
    request_id?: string;
    path?: string;
  };
}

/**
 * Streaming event from SSE
 */
export interface StreamEvent {
  event?: string;
  data: any;
}

/**
 * Chat API client class
 */
export class ChatApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = API_BASE_URL, timeout: number = API_TIMEOUT) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  /**
   * Send a chat message (non-streaming)
   */
  async sendMessage(request: ChatApiRequest): Promise<ChatApiResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    console.log('[ChatAPI] Request →', JSON.stringify(request, null, 2));

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error: ApiError = await response.json();
        console.error('[ChatAPI] Error response ←', error);
        throw new Error(error.error.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ChatApiResponse = await response.json();
      console.log('[ChatAPI] Response ←', JSON.stringify({
        refused: data.refused,
        citations: data.citations?.length ?? 0,
        metadata: data.metadata,
        message_preview: data.message?.slice(0, 120),
      }, null, 2));
      return data;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timed out');
        }
        throw error;
      }
      throw new Error('Unknown error occurred');
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Send a chat message with streaming response (SSE)
   */
  async *sendMessageStream(
    request: ChatApiRequest
  ): AsyncGenerator<StreamEvent, void, unknown> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;

          const event = this.parseSSELine(line);
          if (event) {
            yield event;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Parse SSE line
   */
  private parseSSELine(line: string): StreamEvent | null {
    if (line.startsWith('event:')) {
      // Store event type for next data line
      return { event: line.substring(6).trim(), data: null };
    }

    if (line.startsWith('data:')) {
      const dataStr = line.substring(5).trim();
      try {
        const data = JSON.parse(dataStr);
        return { data };
      } catch {
        return { data: dataStr };
      }
    }

    return null;
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<{
    status: string;
    service: string;
    timestamp: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  }
}

// ---------------------------------------------------------------------------
// T117 — User-friendly error recovery
// ---------------------------------------------------------------------------

/** Maps API error codes (and HTTP status codes) to friendly UI messages. */
const ERROR_MESSAGES: Record<string, string> = {
  // Rate limiting
  rate_limit_exceeded: 'You have reached the request limit. Please wait a moment before trying again.',
  // Validation
  bad_request: 'Your message could not be processed. Please check your input and try again.',
  validation_error: 'Your message contains characters that cannot be processed. Please rephrase.',
  message_too_long: 'Your message is too long. Please shorten it to under 500 characters.',
  // Auth / CAPTCHA
  captcha_required: 'Unusual activity detected. Please complete the security check.',
  captcha_invalid: 'Security check failed. Please try again.',
  unauthorized: 'Authentication required. Please refresh the page.',
  // Service errors
  service_unavailable: 'The chat service is temporarily unavailable. Please try again in a moment.',
  gateway_timeout: 'The response took too long. Please try a shorter question.',
  internal_server_error: 'Something went wrong on our end. Please try again.',
  // Network
  NETWORK_ERROR: 'You appear to be offline. Please check your internet connection.',
  AbortError: 'The request timed out. Please try a shorter or simpler question.',
  // Offline (service worker)
  offline: 'You are offline. Chat requires an internet connection.',
};

/**
 * T117 — Translate a raw API / network error into a UI-ready message.
 *
 * Priority:
 *   1. Exact error code match
 *   2. HTTP status code prefix (e.g. "429" → "rate_limit_exceeded")
 *   3. Partial keyword match in the error message
 *   4. Generic fallback
 */
export function getUserFriendlyError(error: unknown): string {
  if (error instanceof Error) {
    // AbortError from fetch timeout
    if (error.name === 'AbortError' || error.message.includes('timed out')) {
      return ERROR_MESSAGES['AbortError'];
    }
    // Offline (service worker response)
    if (error.message.toLowerCase().includes('offline') || error.message.includes('NETWORK_ERROR')) {
      return ERROR_MESSAGES['NETWORK_ERROR'];
    }
    // Try exact code match from message
    for (const [code, msg] of Object.entries(ERROR_MESSAGES)) {
      if (error.message.includes(code)) return msg;
    }
    // HTTP status code keywords
    if (error.message.includes('429')) return ERROR_MESSAGES['rate_limit_exceeded'];
    if (error.message.includes('503')) return ERROR_MESSAGES['service_unavailable'];
    if (error.message.includes('504')) return ERROR_MESSAGES['gateway_timeout'];
    if (error.message.includes('500')) return ERROR_MESSAGES['internal_server_error'];
  }
  return ERROR_MESSAGES['internal_server_error'];
}

// Export singleton instance
export const chatApi = new ChatApiClient();

/**
 * Helper function to send a chat message.
 * T064 [US2] — Accepts optional selection_context for Selected-Text mode.
 * T086 [US4] — Accepts optional tone string.
 */
export async function sendChatMessage(
  message: string,
  mode: Mode = Mode.BOOK_ONLY,
  filters?: ChatApiRequest['filters'],
  selectionContext?: SelectionContext,
  tone?: string,
): Promise<ChatApiResponse> {
  return chatApi.sendMessage({
    message,
    mode,
    ...(tone ? { tone } : {}),
    filters,
    ...(selectionContext ? { selection_context: selectionContext } : {}),
  });
}

/**
 * Helper function to send a streaming chat message.
 * T064 [US2] — Accepts optional selection_context for Selected-Text mode.
 * T086 [US4] — Accepts optional tone string.
 */
export async function* sendChatMessageStream(
  message: string,
  mode: Mode = Mode.BOOK_ONLY,
  filters?: ChatApiRequest['filters'],
  selectionContext?: SelectionContext,
  tone?: string,
): AsyncGenerator<StreamEvent, void, unknown> {
  yield* chatApi.sendMessageStream({
    message,
    mode,
    ...(tone ? { tone } : {}),
    filters,
    ...(selectionContext ? { selection_context: selectionContext } : {}),
  });
}
