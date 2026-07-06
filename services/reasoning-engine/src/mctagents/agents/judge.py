from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    ClaimScores,
    ClaimStatus,
    Decision,
    Event,
    EventType,
    ThinkingStep,
)

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a JudgeAgent in a claim-centered social reasoning system.

Your job is to objectively score and judge claims based on logic, evidence,
resistance to criticism, and risk.

You MUST return valid JSON with this structure:
{
  "scores": [
    {
      "claim_id": "string - UUID of the claim",
      "logic": 0.0-1.0,
      "evidence": 0.0-1.0,
      "feasibility": 0.0-1.0,
      "critic_resistance": 0.0-1.0,
      "risk_adjusted": 0.0-1.0,
      "verdict": "accepted|rejected|uncertain",
      "rejection_reason": "string or null - if rejected, why"
    }
  ],
  "overall_confidence": 0.0-1.0,
  "needs_more_debate": true/false,
  "debate_reason": "string or null - why more debate is needed"
}

Scoring guidelines:
- logic (0-1): Internal consistency, sound reasoning, no logical fallacies
- evidence (0-1): Strength and relevance of supporting evidence
- feasibility (0-1): Practical implementability
- critic_resistance (0-1): How well the claim holds up against objections
- risk_adjusted (0-1): Score penalized for unaddressed risks

Verdict rules:
- "accepted": final_score >= 0.7 AND no critical unresolved objections
- "rejected": final_score < 0.4 OR has critical objections with no valid defense
- "uncertain": everything in between

needs_more_debate: true if overall confidence < 0.6 AND rounds remaining could help.

Return ONLY the JSON object.\
"""


class JudgeAgent(BaseAgent):
    agent_id = "judge_agent"
    role = "Judging"
    capabilities = ["score_claims", "accept_reject", "determine_consensus"]

    async def act(self, context: AgentContext) -> AgentResult:
        thinking_steps: list[ThinkingStep] = []
        step_seq = 0

        if not context.claims:
            return AgentResult(agent_id=self.agent_id)

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Scoring {len(context.claims)} claims across 5 dimensions.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        claims_summary = "\n".join(
            f"Claim {c.id} (type={c.claim_type.value}, confidence={c.confidence}, "
            f"status={c.status.value}, evidence_status={c.evidence_status.value}):\n"
            f"  Text: {c.text}\n"
            f"  Parent: {c.parent_claim_id or 'none'}"
            for c in context.claims
            if c.status
            not in (
                ClaimStatus.REJECTED.value,
                ClaimStatus.UNCERTAIN.value,
            )
        )

        evidence_summary = ""
        if context.evidence:
            evidence_summary = "\nAvailable evidence:\n" + "\n".join(
                f"- For claim {e.supports_claim_ids}: {e.summary} "
                f"(reliability={e.reliability_score})"
                for e in context.evidence
            )

        objections_summary = ""
        unresolved = [o for o in context.objections if not o.resolved]
        if unresolved:
            objections_summary = "\nUnresolved objections:\n" + "\n".join(
                f"- Against {o.target_claim_id}: {o.reason} "
                f"(severity={o.severity.value}, fix: {o.requested_fix or 'none'})"
                for o in unresolved
            )

        revisions_summary = ""
        if context.revisions:
            revisions_summary = "\nRevisions made:\n" + "\n".join(
                f"- {r.get('reason', 'no reason given')}"
                for r in context.revisions
            )

        user_prompt = (
            "Judge the following claims based on the evidence and criticism.\n\n"
            f"Claims:\n{claims_summary}\n"
            f"{evidence_summary}\n"
            f"{objections_summary}\n"
            f"{revisions_summary}\n\n"
            f"Debate round: {context.debate_round}\n\n"
            "Score each claim and render your verdict."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.3,
            max_tokens=4096,
        )

        parsed = self._parse_response(response.content)
        decision, events = self._build_decision(
            context.run_id, parsed, context,
        )

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Verdict: {len(decision.accepted_claim_ids)} accepted, "
                    f"{len(decision.rejected_claim_ids)} rejected, "
                    f"{len(decision.uncertain_claim_ids)} uncertain.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "judge_scored",
            run_id=context.run_id,
            accepted=len(decision.accepted_claim_ids),
            rejected=len(decision.rejected_claim_ids),
            uncertain=len(decision.uncertain_claim_ids),
            needs_more_debate=decision.needs_more_debate,
        )

        return AgentResult(
            agent_id=self.agent_id,
            events=events,
            thinking_steps=thinking_steps,
            metadata={"decision": decision},
        )

    def _parse_response(self, content: str) -> dict[str, object]:
        try:
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("judge_json_parse_failed", error=str(exc))
            return {
                "scores": [],
                "overall_confidence": 0.0,
                "needs_more_debate": False,
            }

    def _build_decision(
        self,
        run_id: str,
        data: dict[str, object],
        context: AgentContext,
    ) -> tuple[Decision, list[Event]]:
        now = datetime.now(UTC)
        accepted: list[str] = []
        rejected: list[str] = []
        uncertain: list[str] = []
        score_breakdown: dict[str, object] = {}
        claim_status_updates: dict[str, tuple[ClaimStatus, str | None]] = {}

        for item in data.get("scores") or []:
            claim_id = str(item.get("claim_id", ""))
            verdict = str(item.get("verdict", "uncertain")).lower()
            rejection_reason = str(item.get("rejection_reason", "")) or None

            logic = float(item.get("logic", 0.5))
            evidence = float(item.get("evidence", 0.5))
            feasibility = float(item.get("feasibility", 0.5))
            critic_res = float(item.get("critic_resistance", 0.5))
            risk_adj = float(item.get("risk_adjusted", 0.5))

            final_score = (
                logic * 0.25
                + evidence * 0.25
                + feasibility * 0.2
                + critic_res * 0.15
                + risk_adj * 0.15
            )

            scores = ClaimScores(
                logic=logic,
                evidence=evidence,
                feasibility=feasibility,
                critic_resistance=critic_res,
                risk_adjusted=risk_adj,
                final=final_score,
            )

            score_breakdown[claim_id] = {
                "logic": logic,
                "evidence": evidence,
                "feasibility": feasibility,
                "critic_resistance": critic_res,
                "risk_adjusted": risk_adj,
                "final": final_score,
                "verdict": verdict,
                "rejection_reason": rejection_reason,
            }

            if verdict == "accepted":
                accepted.append(claim_id)
                claim_status_updates[claim_id] = (
                    ClaimStatus.ACCEPTED,
                    None,
                )
            elif verdict == "rejected":
                rejected.append(claim_id)
                claim_status_updates[claim_id] = (
                    ClaimStatus.REJECTED,
                    rejection_reason,
                )
            else:
                uncertain.append(claim_id)
                claim_status_updates[claim_id] = (
                    ClaimStatus.UNCERTAIN,
                    None,
                )

        overall_confidence = float(data.get("overall_confidence", 0.5))
        needs_more = bool(data.get("needs_more_debate", False))
        debate_reason = str(data.get("debate_reason", "")) or None

        decision = Decision(
            id=str(uuid.uuid4()),
            run_id=run_id,
            accepted_claim_ids=accepted,
            rejected_claim_ids=rejected,
            uncertain_claim_ids=uncertain,
            score_breakdown=score_breakdown,
            confidence=overall_confidence,
            needs_more_debate=needs_more,
            extra_debate_reason=debate_reason,
            created_at=now,
        )

        events = [
            Event(
                id=str(uuid.uuid4()),
                event_id=f"{run_id}-judge_scored",
                run_id=run_id,
                sequence=0,
                type=EventType.JUDGE_SCORED,
                agent_id=self.agent_id,
                payload={
                    "decision_id": decision.id,
                    "accepted_count": len(accepted),
                    "rejected_count": len(rejected),
                    "uncertain_count": len(uncertain),
                    "confidence": overall_confidence,
                },
            ),
        ]

        return decision, events
