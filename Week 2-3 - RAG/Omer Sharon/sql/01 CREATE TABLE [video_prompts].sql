CREATE TABLE video_prompts (
    id UUID PRIMARY KEY,
    raw_prompt TEXT NOT NULL,
    optimized_prompt TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    category TEXT,
    camera_style TEXT,
    mood TEXT,
    visual_style TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);