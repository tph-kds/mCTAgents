import type { RiskLevel } from "./enums.js";

export interface ProblemFrame {
  id: string;
  run_id: string;
  original_input: string;
  normalized_problem: string;
  constraints: string[];
  success_criteria: string[];
  risk_level: RiskLevel;
  domain: string | null;
  requires_business_decision: boolean;
  requires_research: boolean;
  requires_code: boolean;
  created_at: string;
}
