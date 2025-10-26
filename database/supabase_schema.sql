-- EduCraft Database Schema
-- MSc AI Capstone Project - Supabase PostgreSQL
-- Created: 2025-10-26

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- Stores expert validator information (username-based, no authentication)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast username lookup
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Index for analytics (active users)
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at DESC);

COMMENT ON TABLE users IS 'Expert validators - username-based identification without authentication';
COMMENT ON COLUMN users.username IS 'Primary identifier for tracking syllabi generations';
COMMENT ON COLUMN users.last_active_at IS 'Updated on each login for activity tracking';


-- ============================================================================
-- GENERATED SYLLABI TABLE
-- Stores all generated syllabi with metadata and full JSON
-- Hybrid approach: metadata columns for quick queries + full JSON for completeness
-- ============================================================================
CREATE TABLE IF NOT EXISTS generated_syllabi (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Course metadata (extracted for quick queries)
    title TEXT NOT NULL,
    domain TEXT NOT NULL CHECK (domain IN ('computer_science', 'mathematics', 'physics')),
    level TEXT NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    description TEXT,

    -- Generation metadata
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generation_time_seconds REAL,

    -- Component counts (for analytics without parsing JSON)
    module_count INTEGER,
    activity_count INTEGER,
    assessment_count INTEGER,
    objective_count INTEGER,
    rag_component_count INTEGER,
    generated_component_count INTEGER,

    -- Full syllabus data (JSONB for queryability)
    syllabus_json JSONB NOT NULL
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_syllabi_user_id ON generated_syllabi(user_id);
CREATE INDEX IF NOT EXISTS idx_syllabi_generated_at ON generated_syllabi(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_syllabi_domain_level ON generated_syllabi(domain, level);
CREATE INDEX IF NOT EXISTS idx_syllabi_domain ON generated_syllabi(domain);

-- GIN index for JSONB queries (if needed for advanced analytics)
CREATE INDEX IF NOT EXISTS idx_syllabi_json ON generated_syllabi USING GIN (syllabus_json);

COMMENT ON TABLE generated_syllabi IS 'All generated course syllabi with metadata and full JSON content';
COMMENT ON COLUMN generated_syllabi.syllabus_json IS 'Complete syllabus structure as JSONB for queryability';
COMMENT ON COLUMN generated_syllabi.generation_time_seconds IS 'Time taken by T5 model to generate (for performance analysis)';


-- ============================================================================
-- ANALYTICS VIEWS
-- Pre-computed views for common analytics queries
-- ============================================================================

-- User activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.created_at,
    u.last_active_at,
    COUNT(s.id) AS total_syllabi_generated,
    AVG(s.generation_time_seconds) AS avg_generation_time,
    MIN(s.generated_at) AS first_generation,
    MAX(s.generated_at) AS last_generation
FROM users u
LEFT JOIN generated_syllabi s ON u.id = s.user_id
GROUP BY u.id;

COMMENT ON VIEW user_activity_summary IS 'Summary statistics for each user (for expert validation analysis)';


-- Domain and level distribution
CREATE OR REPLACE VIEW domain_level_distribution AS
SELECT
    domain,
    level,
    COUNT(*) AS syllabus_count,
    AVG(generation_time_seconds) AS avg_time,
    AVG(module_count) AS avg_modules,
    AVG(activity_count) AS avg_activities,
    AVG(assessment_count) AS avg_assessments
FROM generated_syllabi
GROUP BY domain, level
ORDER BY domain, level;

COMMENT ON VIEW domain_level_distribution IS 'Distribution of generated syllabi by domain and difficulty level';


-- Generation performance metrics
CREATE OR REPLACE VIEW generation_performance_metrics AS
SELECT
    DATE_TRUNC('day', generated_at) AS generation_date,
    COUNT(*) AS total_generated,
    AVG(generation_time_seconds) AS avg_time,
    MIN(generation_time_seconds) AS min_time,
    MAX(generation_time_seconds) AS max_time,
    STDDEV(generation_time_seconds) AS stddev_time
FROM generated_syllabi
GROUP BY DATE_TRUNC('day', generated_at)
ORDER BY generation_date DESC;

COMMENT ON VIEW generation_performance_metrics IS 'Daily generation performance statistics';


-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional for future enhancement
-- Currently not enabled to allow simple read/write from app
-- ============================================================================
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE generated_syllabi ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Users can view own data" ON users
--     FOR SELECT USING (auth.uid() = id);

-- CREATE POLICY "Users can view own syllabi" ON generated_syllabi
--     FOR SELECT USING (user_id = auth.uid());


-- ============================================================================
-- SAMPLE DATA (for testing) - Remove in production
-- ============================================================================
-- INSERT INTO users (username, first_name, last_name) VALUES
--     ('test_expert', 'Test', 'Expert');


-- ============================================================================
-- USEFUL QUERIES FOR DISSERTATION ANALYSIS
-- ============================================================================

-- Total syllabi generated
-- SELECT COUNT(*) FROM generated_syllabi;

-- Unique expert participants
-- SELECT COUNT(DISTINCT user_id) FROM generated_syllabi;

-- Syllabi per expert (for validation analysis)
-- SELECT u.username, COUNT(s.id) as count
-- FROM users u
-- LEFT JOIN generated_syllabi s ON u.id = s.user_id
-- GROUP BY u.username
-- ORDER BY count DESC;

-- Domain popularity
-- SELECT domain, COUNT(*) as count,
--        ROUND(AVG(generation_time_seconds)::numeric, 2) as avg_time
-- FROM generated_syllabi
-- GROUP BY domain
-- ORDER BY count DESC;

-- Performance by difficulty level
-- SELECT level,
--        COUNT(*) as count,
--        ROUND(AVG(generation_time_seconds)::numeric, 2) as avg_time,
--        ROUND(AVG(module_count)::numeric, 1) as avg_modules
-- FROM generated_syllabi
-- GROUP BY level
-- ORDER BY
--     CASE level
--         WHEN 'beginner' THEN 1
--         WHEN 'intermediate' THEN 2
--         WHEN 'advanced' THEN 3
--     END;

-- RAG vs Generated component usage
-- SELECT
--     SUM(rag_component_count) as total_rag,
--     SUM(generated_component_count) as total_generated,
--     ROUND(100.0 * SUM(rag_component_count) /
--           (SUM(rag_component_count) + SUM(generated_component_count)), 1) as rag_percentage
-- FROM generated_syllabi;
