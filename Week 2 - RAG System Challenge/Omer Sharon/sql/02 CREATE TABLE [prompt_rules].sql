DROP TABLE IF EXISTS prompt_rules;

CREATE TABLE prompt_rules (
    id UUID PRIMARY KEY,
    rule_name TEXT NOT NULL UNIQUE,
    rule_type TEXT NOT NULL,
    keywords TEXT,
    rule_text TEXT NOT NULL,
    searchable_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX prompt_rules_rule_type_idx ON prompt_rules(rule_type);
