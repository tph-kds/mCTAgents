import type { RunStatus, RunMode, EvidencePolicy } from "./enums.js";
import type { ProblemFrame } from "./problem-frame.js";
import type { Claim } from "./claim.js";
import type { Evidence } from "./evidence.js";
import type { Objection } from "./objection.js";
import type { Revision } from "./revision.js";
import type { Decision } from "./decision.js";
import type { FinalAnswer } from "./final-answer.js";
import type { Event } from "./event.js";

export interface BudgetConfig {
  max_tokens?: number;
  max_cost_usd?: number;
  max_time_seconds?: number;
  max_debate_rounds?: number;
  max_claims?: number;
}

export interface Run {
  id: string;
  tenant_id: string;
  status: RunStatus;
  mode: RunMode;
  evidence_policy: EvidencePolicy;
  budget_config: BudgetConfig;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface RunState {
  run: Run;
  problem_frame: ProblemFrame | null;
  claims: Claim[];
  evidence: Evidence[];
  objections: Objection[];
  revisions: Revision[];
  decisions: Decision[];
  final_answer: FinalAnswer | null;
  events: Event[];
}
