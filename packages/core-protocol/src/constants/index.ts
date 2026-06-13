import type { DebatePolicy } from "../types/debate-policy.js";
import type { AgentRole } from "../types/debate-policy.js";

export const DEFAULT_DEBATE_POLICY: DebatePolicy = {
  max_rounds: 2,
  min_confidence_to_accept: 0.7,
  min_score_to_accept: 0.6,
  require_evidence_for_high_risk: true,
  auto_reject_on_severity: "critical",
  escalation_threshold: 0.3,
  critic_persistence: 2,
  enable_self_improvement: true,
};

export const DEFAULT_AGENT_ROLES: AgentRole[] = [
  {
    id: "architect_agent",
    name: "Architect",
    description: "Proposes architectural decisions and technical approaches",
    focus_areas: ["architecture_decision", "technical_approach", "recommendation"],
    scoring_weights: {
      logic: 0.3,
      evidence: 0.3,
      feasibility: 0.25,
      critic_resistance: 0.15,
    },
  },
  {
    id: "critic_agent",
    name: "Critic",
    description: "Challenges claims with objections and requests evidence",
    focus_areas: ["risk_assessment", "tradeoff_analysis"],
    scoring_weights: {
      logic: 0.25,
      evidence: 0.35,
      feasibility: 0.2,
      critic_resistance: 0.2,
    },
  },
  {
    id: "evidence_agent",
    name: "Evidence Researcher",
    description: "Retrieves and evaluates evidence to support or attack claims",
    focus_areas: ["factual"],
    scoring_weights: {
      logic: 0.15,
      evidence: 0.5,
      feasibility: 0.15,
      critic_resistance: 0.2,
    },
  },
  {
    id: "judge_agent",
    name: "Judge",
    description: "Scores claims and decides which to accept or reject",
    focus_areas: [],
    scoring_weights: {
      logic: 0.3,
      evidence: 0.3,
      feasibility: 0.2,
      critic_resistance: 0.2,
    },
  },
  {
    id: "synthesizer_agent",
    name: "Synthesizer",
    description: "Creates final answers from accepted claims",
    focus_areas: ["recommendation"],
    scoring_weights: {
      logic: 0.25,
      evidence: 0.25,
      feasibility: 0.3,
      critic_resistance: 0.2,
    },
  },
];

export const DEFAULT_SCORING_WEIGHTS = {
  logic: 0.3,
  evidence: 0.3,
  feasibility: 0.2,
  critic_resistance: 0.2,
} as const;

export const MIN_CONFIDENCE_THRESHOLD = 0.5;
export const MAX_CLAIM_LENGTH = 2000;
export const MAX_EVIDENCE_LENGTH = 5000;
