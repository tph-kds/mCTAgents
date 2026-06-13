export const ClaimType = {
  GENERAL: "general",
  ARCHITECTURE_DECISION: "architecture_decision",
  TECHNICAL_APPROACH: "technical_approach",
  RISK_ASSESSMENT: "risk_assessment",
  TRADEOFF_ANALYSIS: "tradeoff_analysis",
  RECOMMENDATION: "recommendation",
  FACTUAL: "factual",
  OPINION: "opinion",
} as const;
export type ClaimType = (typeof ClaimType)[keyof typeof ClaimType];

export const ClaimStatus = {
  PROPOSED: "proposed",
  EVIDENCE_REQUESTED: "evidence_requested",
  SUPPORTED: "supported",
  CHALLENGED: "challenged",
  REVISION_REQUIRED: "revision_required",
  REVISED: "revised",
  ACCEPTED: "accepted",
  REJECTED: "rejected",
  UNCERTAIN: "uncertain",
} as const;
export type ClaimStatus = (typeof ClaimStatus)[keyof typeof ClaimStatus];

export const EvidenceStatus = {
  UNSUPPORTED: "unsupported",
  PARTIAL: "partial",
  SUPPORTED: "supported",
  OVER_SUPPORTED: "over_supported",
} as const;
export type EvidenceStatus = (typeof EvidenceStatus)[keyof typeof EvidenceStatus];

export const SourceType = {
  UPLOADED_DOCUMENT: "uploaded_document",
  OFFICIAL_DOCUMENTATION: "official_documentation",
  WEB_SOURCE: "web_source",
  ACADEMIC_PAPER: "academic_paper",
  GITHUB_REPOSITORY: "github_repository",
  CODE_EXECUTION_RESULT: "code_execution_result",
  DATABASE_RESULT: "database_result",
  INTERNAL_MEMORY: "internal_memory",
  HUMAN_CONFIRMATION: "human_confirmation",
  BENCHMARK_RESULT: "benchmark_result",
} as const;
export type SourceType = (typeof SourceType)[keyof typeof SourceType];

export const Severity = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
} as const;
export type Severity = (typeof Severity)[keyof typeof Severity];

export const RevisionType = {
  OBJECTION_DRIVEN: "objection_driven",
  EVIDENCE_DRIVEN: "evidence_driven",
  JUDGE_FEEDBACK: "judge_feedback",
  SELF_IMPROVEMENT: "self_improvement",
} as const;
export type RevisionType = (typeof RevisionType)[keyof typeof RevisionType];

export const RunStatus = {
  QUEUED: "queued",
  FRAMING: "framing",
  SOCIETY_PLANNING: "society_planning",
  CLAIM_PROPOSAL: "claim_proposal",
  EVIDENCE_ATTACHMENT: "evidence_attachment",
  CRITICISM: "criticism",
  REVISION: "revision",
  JUDGING: "judging",
  ESCALATION: "escalation",
  SYNTHESIS: "synthesis",
  COMPLETED: "completed",
  FAILED: "failed",
  CANCELLED: "cancelled",
} as const;
export type RunStatus = (typeof RunStatus)[keyof typeof RunStatus];

export const EventType = {
  RUN_STARTED: "run_started",
  RUN_FAILED: "run_failed",
  RUN_COMPLETED: "run_completed",
  RUN_CANCELLED: "run_cancelled",
  AGENT_SELECTED: "agent_selected",
  AGENT_STARTED: "agent_started",
  AGENT_COMPLETED: "agent_completed",
  AGENT_ERROR: "agent_error",
  PROBLEM_FRAMED: "problem_framed",
  CLAIM_CREATED: "claim_created",
  CLAIM_UPDATED: "claim_updated",
  EVIDENCE_REQUESTED: "evidence_requested",
  EVIDENCE_ATTACHED: "evidence_attached",
  OBJECTION_CREATED: "objection_created",
  OBJECTION_RESOLVED: "objection_resolved",
  CLAIM_REVISED: "claim_revised",
  JUDGE_SCORED: "judge_scored",
  JUDGE_ESCALATED: "judge_escalated",
  FINAL_ANSWER_CREATED: "final_answer_created",
  EVALUATION_COMPLETED: "evaluation_completed",
  TOOL_CALLED: "tool_called",
  TOOL_RESULT: "tool_result",
} as const;
export type EventType = (typeof EventType)[keyof typeof EventType];

export const EdgeType = {
  PROPOSED: "PROPOSED",
  SUPPORTS: "SUPPORTS",
  ATTACKS: "ATTACKS",
  REVISED_INTO: "REVISED_INTO",
  ACCEPTED: "ACCEPTED",
  REJECTED: "REJECTED",
  USES: "USES",
  PRODUCED: "PRODUCED",
  BACKS: "BACKS",
} as const;
export type EdgeType = (typeof EdgeType)[keyof typeof EdgeType];

export const RiskLevel = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
} as const;
export type RiskLevel = (typeof RiskLevel)[keyof typeof RiskLevel];

export const RunMode = {
  BALANCED_REASONING: "balanced_reasoning",
  FAST_CONSENSUS: "fast_consensus",
  DEEP_ANALYSIS: "deep_analysis",
  ADVERSARIAL: "adversarial",
} as const;
export type RunMode = (typeof RunMode)[keyof typeof RunMode];

export const EvidencePolicy = {
  REQUIRED_FOR_MAJOR_CLAIMS: "required_for_major_claims",
  REQUIRED_FOR_ALL: "required_for_all",
  OPTIONAL: "optional",
} as const;
export type EvidencePolicy = (typeof EvidencePolicy)[keyof typeof EvidencePolicy];

export const DocumentStatus = {
  UPLOADED: "uploaded",
  PROCESSING: "processing",
  PROCESSED: "processed",
  FAILED: "failed",
} as const;
export type DocumentStatus = (typeof DocumentStatus)[keyof typeof DocumentStatus];

export const TraceStatus = {
  OK: "ok",
  ERROR: "error",
  TIMEOUT: "timeout",
} as const;
export type TraceStatus = (typeof TraceStatus)[keyof typeof TraceStatus];

export const ObjectType = {
  CLAIM: "claim",
  EVIDENCE: "evidence",
  OBJECTION: "objection",
  REVISION: "revision",
  DECISION: "decision",
  FINAL_ANSWER: "final_answer",
} as const;
export type ObjectType = (typeof ObjectType)[keyof typeof ObjectType];
