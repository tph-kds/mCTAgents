import type { ClaimType, ClaimStatus, EvidenceStatus } from "./enums.js";

export interface Claim {
  id: string;
  run_id: string;
  author_agent_id: string;
  text: string;
  claim_type: ClaimType;
  confidence: number;
  status: ClaimStatus;
  requires_evidence: boolean;
  evidence_status: EvidenceStatus;
  parent_claim_id: string | null;
  rejection_reason: string | null;
  score_logic: number | null;
  score_evidence: number | null;
  score_feasibility: number | null;
  score_critic_resistance: number | null;
  score_risk_adjusted: number | null;
  score_final: number | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ClaimScores {
  logic: number;
  evidence: number;
  feasibility: number;
  critic_resistance: number;
  risk_adjusted: number;
  final: number;
}
