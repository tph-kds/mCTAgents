export type ClaimType = "general" | "architecture_decision" | "technical_approach" | "risk_assessment" | "tradeoff_analysis" | "recommendation" | "factual" | "opinion";
export type ClaimStatus = "proposed" | "evidence_requested" | "supported" | "challenged" | "revision_required" | "revised" | "accepted" | "rejected" | "uncertain";
export type RunStatus = "queued" | "framing" | "society_planning" | "claim_proposal" | "evidence_attachment" | "criticism" | "revision" | "judging" | "escalation" | "synthesis" | "completed" | "failed" | "cancelled";

export interface Claim { id: string; run_id: string; author_agent_id: string; text: string; claim_type: ClaimType; confidence: number; status: ClaimStatus; evidence_status: string; }
export interface Evidence { id: string; run_id: string; source_type: string; summary: string; reliability_score: number; supports_claim_ids: string[]; attacks_claim_ids: string[]; }
export interface Objection { id: string; run_id: string; target_claim_id: string; author_agent_id: string; reason: string; severity: string; requested_fix: string | null; }
export interface SSEEvent { event_id: string; run_id: string; type: string; sequence: number; agent_id?: string; payload: Record<string, unknown>; created_at: string; }

export interface ThinkingStep {
  step_type: string;
  content: string;
  agent_id: string;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  duration_ms?: number;
  sequence: number;
}