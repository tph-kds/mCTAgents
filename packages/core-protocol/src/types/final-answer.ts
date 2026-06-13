export interface Risk {
  description: string;
  severity: string;
  mitigation: string;
}

export interface FinalAnswer {
  id: string;
  run_id: string;
  answer_text: string;
  accepted_claim_ids: string[];
  rejected_alternatives: string[];
  risks: Risk[];
  next_steps: string[];
  confidence: number;
  metadata: Record<string, unknown>;
  created_at: string;
}
