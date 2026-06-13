import type { SourceType } from "./enums.js";

export interface Evidence {
  id: string;
  run_id: string;
  source_type: SourceType;
  source_ref: string | null;
  summary: string;
  full_text: string | null;
  reliability_score: number;
  source_authority: number | null;
  recency: number | null;
  specificity: number | null;
  independence: number | null;
  retrieval_confidence: number | null;
  chunk_id: string | null;
  document_id: string | null;
  supports_claim_ids: string[];
  attacks_claim_ids: string[];
  metadata: Record<string, unknown>;
  created_at: string;
}
