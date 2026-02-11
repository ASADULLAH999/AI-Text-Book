-- Migration: Create query_logs table
-- Purpose: Track all chatbot queries for analytics and debugging
-- Feature: 002-rag-chatbot
-- Date: 2026-02-10

CREATE TABLE IF NOT EXISTS query_logs (
    -- Primary key
    request_id VARCHAR(255) PRIMARY KEY,

    -- User context
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address INET,

    -- Query details
    query TEXT NOT NULL,
    query_length INTEGER NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('book_only', 'selected_text', 'general_knowledge')),

    -- Context
    chapter_filter VARCHAR(255),
    selected_text TEXT,

    -- Retrieval metrics
    chunks_retrieved INTEGER NOT NULL DEFAULT 0,
    chunks_used INTEGER NOT NULL DEFAULT 0,
    similarity_scores JSONB,

    -- Generation metrics
    model VARCHAR(100) NOT NULL,
    temperature FLOAT,
    response_length INTEGER,
    tokens_used INTEGER,

    -- Performance metrics
    latency_ms INTEGER NOT NULL,
    embedding_latency_ms INTEGER,
    retrieval_latency_ms INTEGER,
    generation_latency_ms INTEGER,
    citation_latency_ms INTEGER,

    -- Response metadata
    citations_count INTEGER DEFAULT 0,
    confidence_avg FLOAT,

    -- Error tracking
    error_code VARCHAR(100),
    error_message TEXT,

    -- Timestamps
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT positive_latency CHECK (latency_ms >= 0),
    CONSTRAINT positive_chunks CHECK (chunks_retrieved >= 0 AND chunks_used >= 0),
    CONSTRAINT valid_confidence CHECK (confidence_avg IS NULL OR (confidence_avg >= 0 AND confidence_avg <= 1))
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_mode ON query_logs(mode);
CREATE INDEX IF NOT EXISTS idx_query_logs_error_code ON query_logs(error_code) WHERE error_code IS NOT NULL;

-- Composite indexes for common analytics queries
CREATE INDEX IF NOT EXISTS idx_query_logs_mode_timestamp ON query_logs(mode, timestamp);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_timestamp ON query_logs(user_id, timestamp);

-- Partial index for error queries
CREATE INDEX IF NOT EXISTS idx_query_logs_errors ON query_logs(timestamp, error_code) WHERE error_code IS NOT NULL;

-- Comments for documentation
COMMENT ON TABLE query_logs IS 'Detailed logs of all chatbot queries for analytics and debugging';
COMMENT ON COLUMN query_logs.request_id IS 'Unique identifier for each request (UUID)';
COMMENT ON COLUMN query_logs.mode IS 'Answering mode: book_only, selected_text, or general_knowledge';
COMMENT ON COLUMN query_logs.similarity_scores IS 'JSON array of similarity scores for retrieved chunks';
COMMENT ON COLUMN query_logs.latency_ms IS 'Total end-to-end latency in milliseconds';
