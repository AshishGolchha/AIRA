-- ==============================================================================
-- AIRA (Autonomous Investment Research Agent) — Initial Schema Migration
-- Target: Supabase PostgreSQL (Postgres 15+ with pgvector)
-- Database: aira_db (Single Primary Relational + Semantic Memory Data Store)
-- ==============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 2. Core Identity & User Preferences
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    alerts_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    investment_focus VARCHAR(255),
    risk_preference VARCHAR(50),
    investment_horizon VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_profiles_user_id UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS ix_user_profiles_user_id ON user_profiles (user_id);

-- ------------------------------------------------------------------------------
-- 3. Investment Portfolio & Watchlist
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    quantity NUMERIC(18, 6) NOT NULL DEFAULT 0.000000,
    average_cost NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_portfolio_user_symbol UNIQUE (user_id, symbol)
);

CREATE INDEX IF NOT EXISTS ix_portfolio_holdings_user_id ON portfolio_holdings (user_id);
CREATE INDEX IF NOT EXISTS ix_portfolio_holdings_symbol ON portfolio_holdings (symbol);

CREATE TABLE IF NOT EXISTS watchlist_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    notes TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_watchlist_user_symbol UNIQUE (user_id, symbol)
);

CREATE INDEX IF NOT EXISTS ix_watchlist_items_user_id ON watchlist_items (user_id);
CREATE INDEX IF NOT EXISTS ix_watchlist_items_symbol ON watchlist_items (symbol);

-- ------------------------------------------------------------------------------
-- 4. Evidence-Grounded AI Research & Intelligence History
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS research_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    facts JSONB NOT NULL DEFAULT '{}'::jsonb,
    fundamentals TEXT,
    valuation TEXT,
    market_context TEXT,
    risks JSONB DEFAULT '[]'::jsonb,
    opportunities JSONB DEFAULT '[]'::jsonb,
    user_context TEXT,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_research_records_user_id ON research_records (user_id);
CREATE INDEX IF NOT EXISTS ix_research_records_symbol ON research_records (symbol);
CREATE INDEX IF NOT EXISTS ix_research_records_created_at ON research_records (created_at DESC);

CREATE TABLE IF NOT EXISTS portfolio_intelligence_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT,
    summary TEXT NOT NULL,
    portfolio_overview TEXT NOT NULL,
    portfolio_risks JSONB DEFAULT '[]'::jsonb,
    portfolio_opportunities JSONB DEFAULT '[]'::jsonb,
    watchlist_priorities JSONB DEFAULT '[]'::jsonb,
    recommended_research JSONB DEFAULT '[]'::jsonb,
    portfolio_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    user_context TEXT,
    facts JSONB NOT NULL DEFAULT '{}'::jsonb,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_portfolio_intelligence_records_user_id ON portfolio_intelligence_records (user_id);
CREATE INDEX IF NOT EXISTS ix_portfolio_intelligence_records_created_at ON portfolio_intelligence_records (created_at DESC);

-- ------------------------------------------------------------------------------
-- 5. Deterministic Investment Alerts & Multi-Channel Notifications
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    facts JSONB DEFAULT '{}'::jsonb,
    sources JSONB DEFAULT '[]'::jsonb,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_dismissed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_alerts_user_id ON alerts (user_id);
CREATE INDEX IF NOT EXISTS ix_alerts_symbol ON alerts (symbol);
CREATE INDEX IF NOT EXISTS ix_alerts_alert_type ON alerts (alert_type);
CREATE INDEX IF NOT EXISTS ix_alerts_is_read ON alerts (is_read);
CREATE INDEX IF NOT EXISTS ix_alerts_is_dismissed ON alerts (is_dismissed);
CREATE INDEX IF NOT EXISTS ix_alerts_created_at ON alerts (created_at DESC);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    in_app_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    email_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    webhook_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    minimum_severity VARCHAR(20) NOT NULL DEFAULT 'info',
    alert_types JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_notification_preferences_user_id UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS ix_notification_preferences_user_id ON notification_preferences (user_id);

CREATE TABLE IF NOT EXISTS notification_endpoints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL DEFAULT 'webhook',
    endpoint_url VARCHAR(500) NOT NULL,
    secret_key VARCHAR(255),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_notification_endpoints_user_id ON notification_endpoints (user_id);

CREATE TABLE IF NOT EXISTS notification_deliveries (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL DEFAULT 'in_app',
    status VARCHAR(50) NOT NULL DEFAULT 'delivered',
    attempt_count INTEGER NOT NULL DEFAULT 1,
    is_retryable BOOLEAN NOT NULL DEFAULT FALSE,
    next_retry_at TIMESTAMPTZ,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    delivered_at TIMESTAMPTZ,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_notification_alert_channel UNIQUE (alert_id, channel)
);

CREATE INDEX IF NOT EXISTS ix_notification_deliveries_alert_id ON notification_deliveries (alert_id);
CREATE INDEX IF NOT EXISTS ix_notification_deliveries_user_id ON notification_deliveries (user_id);
CREATE INDEX IF NOT EXISTS ix_notification_deliveries_status ON notification_deliveries (status);

-- ------------------------------------------------------------------------------
-- 6. Operational Monitoring & Distributed Concurrency Locks
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alert_monitoring_runs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    users_checked INTEGER NOT NULL DEFAULT 0,
    users_succeeded INTEGER NOT NULL DEFAULT 0,
    users_failed INTEGER NOT NULL DEFAULT 0,
    alerts_generated INTEGER NOT NULL DEFAULT 0,
    notifications_attempted INTEGER NOT NULL DEFAULT 0,
    notifications_succeeded INTEGER NOT NULL DEFAULT 0,
    notifications_failed INTEGER NOT NULL DEFAULT 0,
    error_summary TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_alert_monitoring_runs_started_at ON alert_monitoring_runs (started_at DESC);

CREATE TABLE IF NOT EXISTS monitoring_locks (
    name VARCHAR(50) PRIMARY KEY,
    locked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    locked_by VARCHAR(100) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------------------------
-- 7. Semantic Long-Term Vector Memory (pgvector 768-dim)
-- ------------------------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_user_memories_user_id ON user_memories (user_id);
CREATE INDEX IF NOT EXISTS idx_user_memories_created_at ON user_memories (created_at DESC);

-- HNSW Vector Index for fast cosine similarity search
CREATE INDEX IF NOT EXISTS idx_user_memories_embedding
ON user_memories USING hnsw (embedding vector_cosine_ops);

-- User-Scoped Semantic Vector Search RPC Function (SECURITY DEFINER with strict user_id filter)
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
SECURITY DEFINER
SET search_path = public, extensions
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

-- ------------------------------------------------------------------------------
-- 8. Row Level Security (RLS) & API Surface Hardening
-- ------------------------------------------------------------------------------
-- Enable RLS on all 13 application and vector tables to eliminate PostgREST data leakage
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_intelligence_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_endpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_monitoring_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE monitoring_locks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;

-- Revoke all direct PostgREST access from unauthenticated anon and public authenticated roles
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated;

-- Grant full access to service_role (used by MemoryService) and postgres (used by SQLAlchemy)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role, postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role, postgres;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO service_role, postgres;

-- Explicit Idempotent RLS Policies for service_role access across all tables
DROP POLICY IF EXISTS "service_role_all_users" ON users;
CREATE POLICY "service_role_all_users" ON users FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_user_profiles" ON user_profiles;
CREATE POLICY "service_role_all_user_profiles" ON user_profiles FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_portfolio_holdings" ON portfolio_holdings;
CREATE POLICY "service_role_all_portfolio_holdings" ON portfolio_holdings FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_portfolio_intelligence" ON portfolio_intelligence_records;
CREATE POLICY "service_role_all_portfolio_intelligence" ON portfolio_intelligence_records FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_research_records" ON research_records;
CREATE POLICY "service_role_all_research_records" ON research_records FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_watchlist_items" ON watchlist_items;
CREATE POLICY "service_role_all_watchlist_items" ON watchlist_items FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_alerts" ON alerts;
CREATE POLICY "service_role_all_alerts" ON alerts FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_notification_preferences" ON notification_preferences;
CREATE POLICY "service_role_all_notification_preferences" ON notification_preferences FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_notification_endpoints" ON notification_endpoints;
CREATE POLICY "service_role_all_notification_endpoints" ON notification_endpoints FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_notification_deliveries" ON notification_deliveries;
CREATE POLICY "service_role_all_notification_deliveries" ON notification_deliveries FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_alert_monitoring_runs" ON alert_monitoring_runs;
CREATE POLICY "service_role_all_alert_monitoring_runs" ON alert_monitoring_runs FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_monitoring_locks" ON monitoring_locks;
CREATE POLICY "service_role_all_monitoring_locks" ON monitoring_locks FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_user_memories" ON user_memories;
CREATE POLICY "service_role_all_user_memories" ON user_memories FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 9. Alembic Migration Tracking Synchronization
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(255) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num)
VALUES ('0008_create_portfolio_intelligence_records')
ON CONFLICT (version_num) DO NOTHING;
