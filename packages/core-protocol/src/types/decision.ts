export interface Decision {
  id: string;
  run_id: string;
  accepted_claim_ids: string[];
  rejected_claim_ids: string[];
  uncertain_claim_ids: string[];
  score_breakdown: Record<string, unknown>;
  confidence: number;
  needs_more_debate: boolean;
  extra_debate_reason: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}
