-- =============================================================================
-- mCTAgents Database Schema
-- =============================================================================
-- PostgreSQL 16+ required
-- This script initializes the CCSR (Claim-Centered Social Reasoning) schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Runs: A single social reasoning session
-- =============================================================================
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    -- Status: queued, framing, society_planning, claim_proposal, evidence_attachment,
    --         criticism, revision, judging, escalation, synthesis, completed, failed, cancelled
    mode VARCHAR(64) NOT NULL DEFAULT 'balanced_reasoning',
    evidence_policy VARCHAR(64) NOT NULL DEFAULT 'required_for_major_claims',
    budget_config JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_runs_tenant ON runs(tenant_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created ON runs(created_at DESC);

-- =============================================================================
-- ProblemFrames: Normalized problem definition
-- =============================================================================
CREATE TABLE problem_frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    original_input TEXT NOT NULL,
    normalized_problem TEXT NOT NULL,
    constraints JSONB NOT NULL DEFAULT '[]',
    success_criteria JSONB NOT NULL DEFAULT '[]',
    risk_level VARCHAR(16) NOT NULL DEFAULT 'medium',
    domain VARCHAR(64),
    requires_business_decision BOOLEAN DEFAULT FALSE,
    requires_research BOOLEAN DEFAULT FALSE,
    requires_code BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_problem_frames_run ON problem_frames(run_id);

-- =============================================================================
-- Claims: A proposition that can be supported, attacked, revised, accepted, or rejected
-- =============================================================================
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    author_agent_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    claim_type VARCHAR(64) NOT NULL DEFAULT 'general',
    -- Types: general, architecture_decision, technical_approach, risk_assessment,
    --        tradeoff_analysis, recommendation, factual, opinion
    confidence FLOAT NOT NULL DEFAULT 0.5,
    status VARCHAR(32) NOT NULL DEFAULT 'proposed',
    -- Status: proposed, evidence_requested, supported, challenged, revision_required,
    --         revised, accepted, rejected, uncertain
    requires_evidence BOOLEAN DEFAULT FALSE,
    evidence_status VARCHAR(32) DEFAULT 'unsupported',
    -- EvidenceStatus: unsupported, partial, supported, over-supported
    parent_claim_id UUID REFERENCES claims(id),
    rejection_reason TEXT,
    score_logic FLOAT,
    score_evidence FLOAT,
    score_feasibility FLOAT,
    score_critic_resistance FLOAT,
    score_risk_adjusted FLOAT,
    score_final FLOAT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_claims_run ON claims(run_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_parent ON claims(parent_claim_id);
CREATE INDEX idx_claims_author ON claims(author_agent_id);

-- =============================================================================
-- ArgumentEdges: Relationships between claims and other objects
-- =============================================================================
CREATE TABLE argument_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    source_type VARCHAR(32) NOT NULL,
    source_id UUID NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_id UUID NOT NULL,
    edge_type VARCHAR(32) NOT NULL,
    -- EdgeTypes: PROPOSED, SUPPORTS, ATTACKS, REVISED_INTO, ACCEPTED, REJECTED,
    --            USES, PRODUCED, BACKS
    weight FLOAT DEFAULT 1.0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_argument_edges_run ON argument_edges(run_id);
CREATE INDEX idx_argument_edges_source ON argument_edges(source_type, source_id);
CREATE INDEX idx_argument_edges_target ON argument_edges(target_type, target_id);

-- =============================================================================
-- Evidence: Source-backed support or attack item
-- =============================================================================
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    source_type VARCHAR(64) NOT NULL,
    -- SourceTypes: uploaded_document, official_documentation, web_source,
    --              academic_paper, github_repository, code_execution_result,
    --              database_result, internal_memory, human_confirmation, benchmark_result
    source_ref TEXT,
    summary TEXT NOT NULL,
    full_text TEXT,
    reliability_score FLOAT NOT NULL DEFAULT 0.5,
    source_authority FLOAT,
    recency FLOAT,
    specificity FLOAT,
    independence FLOAT,
    retrieval_confidence FLOAT,
    chunk_id UUID,
    document_id UUID,
    supports_claim_ids UUID[] NOT NULL DEFAULT '{}',
    attacks_claim_ids UUID[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_run ON evidence(run_id);
CREATE INDEX idx_evidence_document ON evidence(document_id);

-- =============================================================================
-- Objections: A challenge against a claim
-- =============================================================================
CREATE TABLE objections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    target_claim_id UUID NOT NULL REFERENCES claims(id),
    author_agent_id VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'medium',
    -- Severity: low, medium, high, critical
    requested_fix TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_claim_id UUID REFERENCES claims(id),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_objections_run ON objections(run_id);
CREATE INDEX idx_objections_target ON objections(target_claim_id);

-- =============================================================================
-- Revisions: Claim improvement caused by objections or evidence
-- =============================================================================
CREATE TABLE revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    old_claim_id UUID NOT NULL REFERENCES claims(id),
    new_claim_id UUID NOT NULL REFERENCES claims(id),
    reason TEXT NOT NULL,
    revision_type VARCHAR(32) NOT NULL DEFAULT 'objection_driven',
    -- RevisionTypes: objection_driven, evidence_driven, judge_feedback, self_improvement
    improvement_score FLOAT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_revisions_run ON revisions(run_id);
CREATE INDEX idx_revisions_old_claim ON revisions(old_claim_id);
CREATE INDEX idx_revisions_new_claim ON revisions(new_claim_id);

-- =============================================================================
-- Decisions: Judge output selecting accepted/rejected claims
-- =============================================================================
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    accepted_claim_ids UUID[] NOT NULL DEFAULT '{}',
    rejected_claim_ids UUID[] NOT NULL DEFAULT '{}',
    uncertain_claim_ids UUID[] NOT NULL DEFAULT '{}',
    score_breakdown JSONB NOT NULL DEFAULT '{}',
    confidence FLOAT NOT NULL DEFAULT 0.5,
    needs_more_debate BOOLEAN DEFAULT FALSE,
    extra_debate_reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_decisions_run ON decisions(run_id);

-- =============================================================================
-- FinalAnswers: Synthesized answer referencing accepted claims
-- =============================================================================
CREATE TABLE final_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    accepted_claim_ids UUID[] NOT NULL DEFAULT '{}',
    rejected_alternatives JSONB NOT NULL DEFAULT '[]',
    risks JSONB NOT NULL DEFAULT '[]',
    next_steps JSONB NOT NULL DEFAULT '[]',
    confidence FLOAT NOT NULL DEFAULT 0.5,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_final_answers_run ON final_answers(run_id);

-- =============================================================================
-- Events: Immutable event log for reasoning trace
-- =============================================================================
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(128) NOT NULL UNIQUE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    type VARCHAR(64) NOT NULL,
    -- EventTypes: run_started, run_failed, run_completed, run_cancelled,
    --             agent_selected, agent_started, agent_completed, agent_error,
    --             problem_framed, claim_created, claim_updated,
    --             evidence_requested, evidence_attached,
    --             objection_created, objection_resolved,
    --             claim_revised, judge_scored, judge_escalated,
    --             final_answer_created, evaluation_completed,
    --             tool_called, tool_result
    agent_id VARCHAR(64),
    payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_run ON events(run_id);
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_sequence ON events(run_id, sequence);

-- =============================================================================
-- Documents: Uploaded documents for evidence retrieval
-- =============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    filename TEXT NOT NULL,
    content_type VARCHAR(128),
    size_bytes BIGINT,
    status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
    -- Status: uploaded, processing, processed, failed
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_tenant ON documents(tenant_id);

-- =============================================================================
-- DocumentChunks: For vector search
-- =============================================================================
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    heading TEXT,
    page INTEGER,
    section TEXT,
    token_count INTEGER,
    embedding_id VARCHAR(128),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);

-- =============================================================================
-- AuditLogs: Immutable audit trail
-- =============================================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id UUID,
    details JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- =============================================================================
-- Traces: OpenTelemetry trace spans
-- =============================================================================
CREATE TABLE traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    trace_id VARCHAR(64) NOT NULL,
    span_id VARCHAR(64) NOT NULL,
    parent_span_id VARCHAR(64),
    operation_name VARCHAR(128) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_ms INTEGER,
    status VARCHAR(16) NOT NULL DEFAULT 'ok',
    attributes JSONB NOT NULL DEFAULT '{}',
    events JSONB NOT NULL DEFAULT '[]'
);

CREATE INDEX idx_traces_run ON traces(run_id);
CREATE INDEX idx_traces_trace ON traces(trace_id);

-- =============================================================================
-- Seed Demo Data
-- =============================================================================

-- Insert a demo run
INSERT INTO runs (id, status, mode, evidence_policy) VALUES
    ('11111111-1111-1111-1111-111111111111', 'completed', 'balanced_reasoning', 'required_for_major_claims');

-- Insert a demo problem frame
INSERT INTO problem_frames (run_id, original_input, normalized_problem, constraints, success_criteria, risk_level, domain) VALUES
    ('11111111-1111-1111-1111-111111111111',
     'Should we migrate our monolith to microservices?',
     'Design a migration strategy from monolithic architecture to microservices for a growing engineering team.',
     '["minimize disruption", "preserve existing functionality", "enable independent deployments"]',
     '["clear migration path", "risk assessment", "cost-benefit analysis"]',
     'high',
     'software');

-- Insert demo claims
INSERT INTO claims (run_id, author_agent_id, text, claim_type, confidence, status, requires_evidence, evidence_status) VALUES
    ('11111111-1111-1111-1111-111111111111', 'architect_agent', 'We should adopt a strangler fig pattern for gradual migration.', 'architecture_decision', 0.85, 'accepted', true, 'supported'),
    ('11111111-1111-1111-1111-111111111111', 'architect_agent', 'Start with the user authentication module as the first microservice.', 'technical_approach', 0.78, 'accepted', true, 'supported'),
    ('11111111-1111-1111-1111-111111111111', 'architect_agent', 'We need a service mesh for inter-service communication.', 'recommendation', 0.65, 'rejected', true, 'partial');

-- Insert demo evidence
INSERT INTO evidence (run_id, source_type, summary, reliability_score, supports_claim_ids) VALUES
    ('11111111-1111-1111-1111-111111111111', 'official_documentation', 'Martin Fowler recommends strangler fig pattern for legacy migrations.', 0.9, ARRAY[(SELECT id FROM claims WHERE text LIKE '%strangler fig%' LIMIT 1)]),
    ('11111111-1111-1111-1111-111111111111', 'academic_paper', 'Case studies show 73% success rate with gradual migration approaches.', 0.85, ARRAY[(SELECT id FROM claims WHERE text LIKE '%strangler fig%' LIMIT 1)]);

-- Insert demo objections
INSERT INTO objections (run_id, target_claim_id, author_agent_id, reason, severity, requested_fix) VALUES
    ('11111111-1111-1111-1111-111111111111',
     (SELECT id FROM claims WHERE text LIKE '%service mesh%' LIMIT 1),
     'critic_agent',
     'Service mesh adds significant operational complexity for a team new to microservices.',
     'high',
     'Consider simpler alternatives like API gateway or direct HTTP calls initially.');

-- Insert demo final answer
INSERT INTO final_answers (run_id, answer_text, accepted_claim_ids, risks, next_steps, confidence) VALUES
    ('11111111-1111-1111-1111-111111111111',
     'Adopt a strangler fig pattern for gradual migration, starting with user authentication. Avoid service mesh initially due to operational complexity.',
     ARRAY[(SELECT id FROM claims WHERE text LIKE '%strangler fig%' LIMIT 1), (SELECT id FROM claims WHERE text LIKE '%user authentication%' LIMIT 1)],
     '[{"description": "Migration may take longer than expected", "severity": "medium", "mitigation": "Set clear milestones and regular reviews"}]',
     '["Set up CI/CD pipeline for microservices", "Create API gateway", "Document service boundaries"]',
     0.82);

-- Insert demo events
INSERT INTO events (event_id, run_id, sequence, type, agent_id, payload) VALUES
    ('evt_001', '11111111-1111-1111-1111-111111111111', 1, 'run_started', NULL, '{"problem": "Should we migrate our monolith to microservices?"}'),
    ('evt_002', '11111111-1111-1111-1111-111111111111', 2, 'problem_framed', 'problem_framer', '{}'),
    ('evt_003', '11111111-1111-1111-1111-111111111111', 3, 'claim_created', 'architect_agent', '{}'),
    ('evt_004', '11111111-1111-1111-1111-111111111111', 4, 'evidence_attached', 'evidence_agent', '{}'),
    ('evt_005', '11111111-1111-1111-1111-111111111111', 5, 'objection_created', 'critic_agent', '{}'),
    ('evt_006', '11111111-1111-1111-1111-111111111111', 6, 'judge_scored', 'judge_agent', '{}'),
    ('evt_007', '11111111-1111-1111-1111-111111111111', 7, 'final_answer_created', 'synthesizer_agent', '{}'),
    ('evt_008', '11111111-1111-1111-1111-111111111111', 8, 'run_completed', NULL, '{}');
