CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_systems (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    fintech_segment TEXT NOT NULL DEFAULT 'Lendingtech',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY,
    ai_system_id UUID NOT NULL REFERENCES ai_systems(id),
    pillar TEXT NOT NULL,
    practice TEXT NOT NULL,
    use_case TEXT NOT NULL,
    aggregate_score INTEGER NOT NULL CHECK (aggregate_score BETWEEN 0 AND 100),
    aggregate_risk_level TEXT NOT NULL CHECK (aggregate_risk_level IN ('Low', 'Medium', 'High')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE test_results (
    id UUID PRIMARY KEY,
    evaluation_id UUID NOT NULL REFERENCES evaluations(id),
    test_name TEXT NOT NULL,
    test_type TEXT NOT NULL CHECK (test_type IN ('light', 'strong')),
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    insight TEXT NOT NULL,
    recommendations JSONB NOT NULL,
    metadata JSONB NOT NULL
);

CREATE TABLE benchmark_distributions (
    id UUID PRIMARY KEY,
    distribution_key TEXT NOT NULL,
    anonymized_segment TEXT,
    sample_count INTEGER NOT NULL,
    score_average NUMERIC(5,2) NOT NULL,
    score_p25 NUMERIC(5,2),
    score_p50 NUMERIC(5,2),
    score_p75 NUMERIC(5,2),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

