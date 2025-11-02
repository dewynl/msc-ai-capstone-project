-- Supabase Table Schema for Syllabus Feedback System
-- Run this in your Supabase SQL editor to create the feedback table

CREATE TABLE IF NOT EXISTS syllabus_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    syllabus_id UUID NOT NULL REFERENCES generated_syllabi(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quality_score INTEGER NOT NULL CHECK (quality_score >= 1 AND quality_score <= 10),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,

    -- Ensure user can only rate a syllabus once
    UNIQUE(syllabus_id, user_id)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_feedback_syllabus ON syllabus_feedback(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON syllabus_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_quality ON syllabus_feedback(quality_score);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON syllabus_feedback(created_at);

-- Enable Row Level Security
ALTER TABLE syllabus_feedback ENABLE ROW LEVEL SECURITY;

-- Policy: Allow inserts for authenticated and service role
CREATE POLICY "Allow feedback inserts"
    ON syllabus_feedback FOR INSERT
    WITH CHECK (true);

-- Policy: Anyone can view feedback (for analytics)
CREATE POLICY "Anyone can view feedback"
    ON syllabus_feedback FOR SELECT
    USING (true);

-- Policy: Allow updates (for future enhancement)
CREATE POLICY "Allow feedback updates"
    ON syllabus_feedback FOR UPDATE
    USING (true);

-- Comments
COMMENT ON TABLE syllabus_feedback IS 'User ratings and feedback for generated syllabi';
COMMENT ON COLUMN syllabus_feedback.quality_score IS 'User rating from 1 (poor) to 10 (excellent)';
COMMENT ON COLUMN syllabus_feedback.comments IS 'Optional text feedback from user';
