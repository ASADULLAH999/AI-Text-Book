-- Migration: Create chunk_metadata table
-- Purpose: Store metadata for textbook chunks indexed in Qdrant
-- Feature: 002-rag-chatbot
-- Date: 2026-02-10

CREATE TABLE IF NOT EXISTS chunk_metadata (
    -- Primary key
    chunk_id VARCHAR(255) PRIMARY KEY,

    -- Content metadata
    chapter VARCHAR(255) NOT NULL,
    section VARCHAR(255) NOT NULL,
    heading VARCHAR(500),
    page_number INTEGER,

    -- Chunk statistics
    word_count INTEGER NOT NULL,
    token_count INTEGER,

    -- Textbook location
    file_path TEXT NOT NULL,
    start_offset INTEGER,
    end_offset INTEGER,

    -- Vector database reference
    qdrant_point_id UUID,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes for common queries
    CONSTRAINT positive_word_count CHECK (word_count > 0)
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_chapter ON chunk_metadata(chapter);
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_section ON chunk_metadata(section);
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_created_at ON chunk_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_qdrant_point_id ON chunk_metadata(qdrant_point_id);

-- Composite index for chapter + section queries
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_chapter_section ON chunk_metadata(chapter, section);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chunk_metadata_updated_at
    BEFORE UPDATE ON chunk_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE chunk_metadata IS 'Metadata for textbook chunks stored in Qdrant vector database';
COMMENT ON COLUMN chunk_metadata.chunk_id IS 'Unique identifier for the chunk (format: chapter_section_index)';
COMMENT ON COLUMN chunk_metadata.qdrant_point_id IS 'Reference to the point ID in Qdrant collection';
COMMENT ON COLUMN chunk_metadata.file_path IS 'Original markdown file path in the textbook';
