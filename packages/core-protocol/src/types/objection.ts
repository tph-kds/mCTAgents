import type { Severity } from "./enums.js";

export interface Objection {
  id: string;
  run_id: string;
  target_claim_id: string;
  author_agent_id: string;
  reason: string;
  severity: Severity;
  requested_fix: string | null;
  resolved: boolean;
  resolution_claim_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}
