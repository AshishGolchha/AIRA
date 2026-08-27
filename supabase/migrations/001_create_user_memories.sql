-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create user_memories table for semantic long-term memory
CREATE TABLE IF NOT EXISTS user_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    memory_type TEXT NOT NULL DEFAULT 'preference',
    importance TEXT NOT NULL DEFAULT 'medium',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index user_id for strict per-user queries
CREATE INDEX IF NOT EXISTS idx_user_memories_user_id ON user_memories (user_id);
CREATE INDEX IF NOT EXISTS idx_user_memories_created_at ON user_memories (created_at DESC);

-- HNSW Vector Index for fast cosine similarity search
CREATE INDEX IF NOT EXISTS idx_user_memories_embedding
ON user_memories USING hnsw (embedding vector_cosine_ops);

-- User-Scoped Semantic Search RPC Function
CREATE OR REPLACE FUNCTION match_user_memories (
    p_user_id INTEGER,
    p_embedding vector(768),
    p_match_threshold FLOAT DEFAULT 0.5,
    p_match_count INT DEFAULT 5,
    p_memory_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    user_id INTEGER,
    content TEXT,
    memory_type TEXT,
    importance TEXT,
    metadata JSONB,
    similarity FLOAT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.user_id,
        m.content,
        m.memory_type,
        m.importance,
        m.metadata,
        (1 - (m.embedding <=> p_embedding))::FLOAT AS similarity,
        m.created_at,
        m.updated_at
    FROM user_memories m
    WHERE m.user_id = p_user_id
      AND (p_memory_type IS NULL OR m.memory_type = p_memory_type)
      AND (1 - (m.embedding <=> p_embedding)) >= p_match_threshold
    ORDER BY m.embedding <=> p_embedding
    LIMIT p_match_count;
END;
$$;
