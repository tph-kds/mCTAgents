import type { Severity } from "./enums.js";

export interface DebatePolicy {
  max_rounds: number;
  min_confidence_to_accept: number;
  min_score_to_accept: number;
  require_evidence_for_high_risk: boolean;
  auto_reject_on_severity: Severity;
  escalation_threshold: number;
  critic_persistence: number;
  enable_self_improvement: boolean;
}

export interface AgentRole {
  id: string;
  name: string;
  description: string;
  focus_areas: string[];
  scoring_weights: {
    logic: number;
    evidence: number;
    feasibility: number;
    critic_resistance: number;
  };
}
