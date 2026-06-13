import type { RevisionType } from "./enums.js";

export interface Revision {
  id: string;
  run_id: string;
  old_claim_id: string;
  new_claim_id: string;
  reason: string;
  revision_type: RevisionType;
  improvement_score: number | null;
  metadata: Record<string, unknown>;
  created_at: string;
}
