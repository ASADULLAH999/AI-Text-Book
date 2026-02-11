/**
 * TypeScript types for chat API
 * Mirrors backend API contracts from shared/openapi.yaml
 */

/**
 * Answering mode for the chatbot
 */
export enum AnswerMode {
  BOOK_ONLY = 'book_only',
  SELECTED_TEXT = 'selected_text',
  GENERAL_KNOWLEDGE = 'general_knowledge',
}

/**
 * Context for the user query
 */
export interface QueryContext {
  /** User-selected text for Selected-Text mode */
  selected_text?: string | null;
  /** Restrict search to specific chapter (e.g., 'Chapter 3') */
  chapter_filter?: string | null;
  /** Session identifier for analytics tracking */
  session_id?: string | null;
}

/**
 * Configuration options for retrieval
 */
export interface QueryOptions {
  /** Number of chunks to retrieve before reranking (5-20) */
  top_k?: number;
  /** Minimum cosine similarity for chunk inclusion (0.5-1.0) */
  similarity_threshold?: number;
  /** Include citation metadata in response */
  include_citations?: boolean;
}

/**
 * Request for chat endpoint
 */
export interface ChatRequest {
  /** User question (max 500 characters) */
  query: string;
  /** Answering mode (default: book_only) */
  mode?: AnswerMode;
  /** Additional query context */
  context?: QueryContext;
  /** Retrieval configuration options */
  options?: QueryOptions;
}

/**
 * Confidence level for citation
 */
export enum ConfidenceLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

/**
 * Citation source with metadata
 */
export interface Source {
  /** Unique chunk identifier */
  chunk_id: string;
  /** Source chapter */
  chapter: string;
  /** Source section */
  section: string;
  /** Heading title */
  title: string;
  /** Confidence score (0.0-1.0) */
  confidence: number;
  /** Human-readable confidence level */
  confidence_level: ConfidenceLevel;
  /** Text excerpt from chunk (max 500 chars) */
  excerpt: string;
}

/**
 * Metadata about the response generation
 */
export interface ResponseMetadata {
  /** Unique request identifier for tracing */
  request_id: string;
  /** Total response time in milliseconds */
  latency_ms: number;
  /** Number of chunks retrieved from vector search */
  chunks_retrieved: number;
  /** Number of chunks used in final answer generation */
  chunks_used: number;
  /** LLM model used for generation */
  model: string;
  /** Embedding model used */
  embeddings_model: string;
}

/**
 * Response from chat endpoint
 */
export interface ChatResponse {
  /** Generated answer text */
  answer: string;
  /** Mode used to generate answer */
  mode: AnswerMode;
  /** Citation sources (empty if mode=general_knowledge) */
  sources: Source[];
  /** Response metadata for monitoring */
  metadata: ResponseMetadata;
}

/**
 * Error codes for API responses
 */
export enum ErrorCode {
  RETRIEVAL_FAILED = 'RETRIEVAL_FAILED',
  GENERATION_FAILED = 'GENERATION_FAILED',
  INVALID_MODE = 'INVALID_MODE',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INSUFFICIENT_CONTEXT = 'INSUFFICIENT_CONTEXT',
  AMBIGUOUS_QUERY = 'AMBIGUOUS_QUERY',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
}

/**
 * Detailed error information
 */
export interface ErrorDetail {
  /** Machine-readable error code */
  code: ErrorCode;
  /** Human-readable error message */
  message: string;
  /** Additional context about the error */
  details: string;
  /** Error timestamp */
  timestamp: string;
  /** Request ID for tracing */
  request_id: string;
}

/**
 * Standardized error response
 */
export interface ErrorResponse {
  /** Error details */
  error: ErrorDetail;
}

/**
 * Health check response
 */
export interface HealthResponse {
  /** Overall service health status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** API version */
  version: string;
  /** Current server timestamp */
  timestamp: string;
  /** Dependency health status */
  dependencies: {
    qdrant: 'connected' | 'disconnected';
    postgres: 'connected' | 'disconnected';
    openai: 'available' | 'unavailable';
  };
  /** Warning messages for degraded status */
  warnings?: string[];
  /** Error messages for unhealthy status */
  errors?: string[];
  /** Server uptime in seconds */
  uptime_seconds?: number;
}
