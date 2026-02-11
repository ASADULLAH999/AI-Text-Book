-- Migration: Create analytics table
-- Purpose: Aggregated metrics for monitoring and dashboards
-- Feature: 002-rag-chatbot
-- Date: 2026-02-10

CREATE TABLE IF NOT EXISTS analytics (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Time window
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    window_size VARCHAR(20) NOT NULL CHECK (window_size IN ('1min', '5min', '1hour', '1day')),

    -- Query volume
    total_queries INTEGER NOT NULL DEFAULT 0,
    successful_queries INTEGER NOT NULL DEFAULT 0,
    failed_queries INTEGER NOT NULL DEFAULT 0,

    -- Mode distribution
    book_only_queries INTEGER NOT NULL DEFAULT 0,
    selected_text_queries INTEGER NOT NULL DEFAULT 0,
    general_knowledge_queries INTEGER NOT NULL DEFAULT 0,

    -- Performance metrics
    avg_latency_ms FLOAT,
    p50_latency_ms FLOAT,
    p95_latency_ms FLOAT,
    p99_latency_ms FLOAT,
    max_latency_ms INTEGER,

    -- Retrieval metrics
    avg_chunks_retrieved FLOAT,
    avg_chunks_used FLOAT,
    avg_similarity_score FLOAT,

    -- Citation metrics
    avg_citations_per_query FLOAT,
    avg_confidence_score FLOAT,

    -- Error metrics
    error_rate FLOAT,
    top_errors JSONB,

    -- User metrics
    unique_users INTEGER,
    unique_sessions INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_window CHECK (window_end > window_start),
    CONSTRAINT positive_queries CHECK (total_queries >= 0),
    CONSTRAINT valid_error_rate CHECK (error_rate >= 0 AND error_rate <= 1),
    CONSTRAINT unique_time_window UNIQUE (window_start, window_end, window_size)
);

-- Indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_analytics_window_start ON analytics(window_start);
CREATE INDEX IF NOT EXISTS idx_analytics_window_size ON analytics(window_size);
CREATE INDEX IF NOT EXISTS idx_analytics_window_size_start ON analytics(window_size, window_start);

-- Materialized view for real-time dashboard (last 24 hours)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics_dashboard AS
SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    mode,
    COUNT(*) AS query_count,
    AVG(latency_ms)::INTEGER AS avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INTEGER AS p95_latency_ms,
    AVG(chunks_retrieved)::INTEGER AS avg_chunks_retrieved,
    AVG(CASE WHEN error_code IS NOT NULL THEN 1 ELSE 0 END) AS error_rate,
    COUNT(DISTINCT user_id) AS unique_users
FROM query_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour, mode
ORDER BY hour DESC, mode;

-- Index on the materialized view
CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_hour ON analytics_dashboard(hour);

-- Refresh function for the materialized view
CREATE OR REPLACE FUNCTION refresh_analytics_dashboard()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY analytics_dashboard;
END;
$$ LANGUAGE plpgsql;

-- Function to compute analytics for a time window
CREATE OR REPLACE FUNCTION compute_analytics(
    p_window_start TIMESTAMPTZ,
    p_window_end TIMESTAMPTZ,
    p_window_size VARCHAR(20)
)
RETURNS void AS $$
DECLARE
    v_total_queries INTEGER;
    v_successful_queries INTEGER;
    v_failed_queries INTEGER;
    v_book_only INTEGER;
    v_selected_text INTEGER;
    v_general_knowledge INTEGER;
    v_avg_latency FLOAT;
    v_p50_latency FLOAT;
    v_p95_latency FLOAT;
    v_p99_latency FLOAT;
    v_max_latency INTEGER;
    v_avg_chunks_retrieved FLOAT;
    v_avg_chunks_used FLOAT;
    v_avg_similarity FLOAT;
    v_avg_citations FLOAT;
    v_avg_confidence FLOAT;
    v_error_rate FLOAT;
    v_unique_users INTEGER;
    v_unique_sessions INTEGER;
BEGIN
    -- Compute aggregated metrics
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE error_code IS NULL),
        COUNT(*) FILTER (WHERE error_code IS NOT NULL),
        COUNT(*) FILTER (WHERE mode = 'book_only'),
        COUNT(*) FILTER (WHERE mode = 'selected_text'),
        COUNT(*) FILTER (WHERE mode = 'general_knowledge'),
        AVG(latency_ms),
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms),
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms),
        MAX(latency_ms),
        AVG(chunks_retrieved),
        AVG(chunks_used),
        AVG((similarity_scores->0->>'score')::FLOAT),
        AVG(citations_count),
        AVG(confidence_avg),
        AVG(CASE WHEN error_code IS NOT NULL THEN 1 ELSE 0 END),
        COUNT(DISTINCT user_id),
        COUNT(DISTINCT session_id)
    INTO
        v_total_queries,
        v_successful_queries,
        v_failed_queries,
        v_book_only,
        v_selected_text,
        v_general_knowledge,
        v_avg_latency,
        v_p50_latency,
        v_p95_latency,
        v_p99_latency,
        v_max_latency,
        v_avg_chunks_retrieved,
        v_avg_chunks_used,
        v_avg_similarity,
        v_avg_citations,
        v_avg_confidence,
        v_error_rate,
        v_unique_users,
        v_unique_sessions
    FROM query_logs
    WHERE timestamp >= p_window_start AND timestamp < p_window_end;

    -- Insert or update analytics record
    INSERT INTO analytics (
        window_start, window_end, window_size,
        total_queries, successful_queries, failed_queries,
        book_only_queries, selected_text_queries, general_knowledge_queries,
        avg_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms, max_latency_ms,
        avg_chunks_retrieved, avg_chunks_used, avg_similarity_score,
        avg_citations_per_query, avg_confidence_score,
        error_rate, unique_users, unique_sessions
    ) VALUES (
        p_window_start, p_window_end, p_window_size,
        v_total_queries, v_successful_queries, v_failed_queries,
        v_book_only, v_selected_text, v_general_knowledge,
        v_avg_latency, v_p50_latency, v_p95_latency, v_p99_latency, v_max_latency,
        v_avg_chunks_retrieved, v_avg_chunks_used, v_avg_similarity,
        v_avg_citations, v_avg_confidence,
        v_error_rate, v_unique_users, v_unique_sessions
    )
    ON CONFLICT (window_start, window_end, window_size)
    DO UPDATE SET
        total_queries = EXCLUDED.total_queries,
        successful_queries = EXCLUDED.successful_queries,
        failed_queries = EXCLUDED.failed_queries,
        book_only_queries = EXCLUDED.book_only_queries,
        selected_text_queries = EXCLUDED.selected_text_queries,
        general_knowledge_queries = EXCLUDED.general_knowledge_queries,
        avg_latency_ms = EXCLUDED.avg_latency_ms,
        p50_latency_ms = EXCLUDED.p50_latency_ms,
        p95_latency_ms = EXCLUDED.p95_latency_ms,
        p99_latency_ms = EXCLUDED.p99_latency_ms,
        max_latency_ms = EXCLUDED.max_latency_ms,
        avg_chunks_retrieved = EXCLUDED.avg_chunks_retrieved,
        avg_chunks_used = EXCLUDED.avg_chunks_used,
        avg_similarity_score = EXCLUDED.avg_similarity_score,
        avg_citations_per_query = EXCLUDED.avg_citations_per_query,
        avg_confidence_score = EXCLUDED.avg_confidence_score,
        error_rate = EXCLUDED.error_rate,
        unique_users = EXCLUDED.unique_users,
        unique_sessions = EXCLUDED.unique_sessions;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE analytics IS 'Aggregated metrics for monitoring dashboards and alerting';
COMMENT ON COLUMN analytics.window_size IS 'Time window size: 1min, 5min, 1hour, or 1day';
COMMENT ON FUNCTION compute_analytics IS 'Compute and store aggregated analytics for a time window';
COMMENT ON MATERIALIZED VIEW analytics_dashboard IS 'Real-time dashboard data (last 24 hours, refreshed every 5 minutes)';
