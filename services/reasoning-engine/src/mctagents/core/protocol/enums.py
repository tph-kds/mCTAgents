from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = "queued"
    FRAMING = "framing"
    SOCIETY_PLANNING = "society_planning"
    CLAIM_PROPOSAL = "claim_proposal"
    EVIDENCE_ATTACHMENT = "evidence_attachment"
    CRITICISM = "criticism"
    REVISION = "revision"
    JUDGING = "judging"
    ESCALATION = "escalation"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunMode(StrEnum):
    FAST = "fast"
    BALANCED_REASONING = "balanced_reasoning"
    DEEP_ANALYSIS = "deep_analysis"
    ADVERSARIAL = "adversarial"
    CONSENSUS_BUILDING = "consensus_building"


class EvidencePolicy(StrEnum):
    ALWAYS_REQUIRED = "always_required"
    REQUIRED_FOR_MAJOR_CLAIMS = "required_for_major_claims"
    OPTIONAL = "optional"
    ON_DEMAND = "on_demand"


class ClaimType(StrEnum):
    GENERAL = "general"
    ARCHITECTURE_DECISION = "architecture_decision"
    TECHNICAL_APPROACH = "technical_approach"
    RISK_ASSESSMENT = "risk_assessment"
    TRADEOFF_ANALYSIS = "tradeoff_analysis"
    RECOMMENDATION = "recommendation"
    FACTUAL = "factual"
    OPINION = "opinion"


class ClaimStatus(StrEnum):
    PROPOSED = "proposed"
    EVIDENCE_REQUESTED = "evidence_requested"
    SUPPORTED = "supported"
    CHALLENGED = "challenged"
    REVISION_REQUIRED = "revision_required"
    REVISED = "revised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"


class EvidenceStatus(StrEnum):
    UNSUPPORTED = "unsupported"
    PARTIAL = "partial"
    SUPPORTED = "supported"
    OVER_SUPPORTED = "over-supported"


class SourceType(StrEnum):
    UPLOADED_DOCUMENT = "uploaded_document"
    OFFICIAL_DOCUMENTATION = "official_documentation"
    WEB_SOURCE = "web_source"
    ACADEMIC_PAPER = "academic_paper"
    GITHUB_REPOSITORY = "github_repository"
    CODE_EXECUTION_RESULT = "code_execution_result"
    DATABASE_RESULT = "database_result"
    INTERNAL_MEMORY = "internal_memory"
    HUMAN_CONFIRMATION = "human_confirmation"
    BENCHMARK_RESULT = "benchmark_result"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RevisionType(StrEnum):
    OBJECTION_DRIVEN = "objection_driven"
    EVIDENCE_DRIVEN = "evidence_driven"
    JUDGE_FEEDBACK = "judge_feedback"
    SELF_IMPROVEMENT = "self_improvement"


class EventType(StrEnum):
    RUN_STARTED = "run_started"
    RUN_FAILED = "run_failed"
    RUN_COMPLETED = "run_completed"
    RUN_CANCELLED = "run_cancelled"
    AGENT_SELECTED = "agent_selected"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    PROBLEM_FRAMED = "problem_framed"
    CLAIM_CREATED = "claim_created"
    CLAIM_UPDATED = "claim_updated"
    EVIDENCE_REQUESTED = "evidence_requested"
    EVIDENCE_ATTACHED = "evidence_attached"
    OBJECTION_CREATED = "objection_created"
    OBJECTION_RESOLVED = "objection_resolved"
    CLAIM_REVISED = "claim_revised"
    JUDGE_SCORED = "judge_scored"
    JUDGE_ESCALATED = "judge_escalated"
    FINAL_ANSWER_CREATED = "final_answer_created"
    EVALUATION_COMPLETED = "evaluation_completed"
    TOOL_CALLED = "tool_called"
    TOOL_RESULT = "tool_result"


class EdgeType(StrEnum):
    PROPOSED = "PROPOSED"
    SUPPORTS = "SUPPORTS"
    ATTACKS = "ATTACKS"
    REVISED_INTO = "REVISED_INTO"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    USES = "USES"
    PRODUCED = "PRODUCED"
    BACKS = "BACKS"


class EdgeEntityType(StrEnum):
    CLAIM = "claim"
    EVIDENCE = "evidence"
    OBJECTION = "objection"
    REVISION = "revision"
    DECISION = "decision"
    FINAL_ANSWER = "final_answer"
    EVENT = "event"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class TraceStatus(StrEnum):
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
