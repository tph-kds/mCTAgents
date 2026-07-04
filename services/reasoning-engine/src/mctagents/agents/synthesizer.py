from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    Event,
    EventType,
    FinalAnswer,
    RiskItem,
    ThinkingStep,
)

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a SynthesizerAgent in a claim-centered social reasoning system.

Your job is to produce a final answer by synthesizing accepted claims into a
coherent, actionable response.

You MUST return valid JSON with this structure:
{
  "answer_text": "string - comprehensive final answer in markdown",
  "rejected_alternatives": [
    {
      "claim_text": "string - the rejected claim",
      "reason": "string - why it was rejected"
    }
  ],
  "risks": [
    {
      "description": "string - risk description",
      "severity": "low|medium|high|critical",
      "mitigation": "string or null - suggested mitigation"
    }
  ],
  "next_steps": ["string - actionable follow-up items"]
}

Rules:
- Base your answer ONLY on accepted claims. Do not introduce new assertions.
- Clearly state what was considered but rejected, and why.
- Be honest about remaining risks and uncertainty.
- Next steps should be specific and actionable.
- Write in clear, professional prose.
- Return ONLY the JSON object.\
"""


class SynthesizerAgent(BaseAgent):
    agent_id = "synthesizer_agent"
    role = "Synthesis"
    capabilities = ["create_final_answer", "summarize_reasoning"]

    async def act(self, context: AgentContext) -> AgentResult:
        thinking_steps: list[ThinkingStep] = []
        step_seq = 0

        decision = context.metadata.get("decision")
        if decision is None:
            logger.warning("no_decision_to_synthesize", run_id=context.run_id)
            return AgentResult(agent_id=self.agent_id)

        accepted = [
            c
            for c in context.claims
            if c.id in decision.accepted_claim_ids
        ]

        rejected = [
            c
            for c in context.claims
            if c.id in decision.rejected_claim_ids
        ]

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Synthesizing final answer from {len(accepted)} accepted claims.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        accepted_summary = "\n".join(
            f"- [{c.claim_type.value}] {c.text} "
            f"(confidence: {c.confidence}, "
            f"score: {decision.score_breakdown.get(c.id, {}).get('final', 'N/A')})"
            for c in accepted
        )

        rejected_summary = ""
        if rejected:
            rejected_summary = "\nRejected claims:\n" + "\n".join(
                f"- {c.text} - "
                f"{decision.score_breakdown.get(c.id, {}).get('rejection_reason', 'no reason')}"
                for c in rejected
            )

        evidence_summary = ""
        if context.evidence:
            evidence_summary = "\nEvidence considered:\n" + "\n".join(
                f"- {e.summary} (reliability={e.reliability_score})"
                for e in context.evidence
                if e.supports_claim_ids
            )

        unresolved_objections = [o for o in context.objections if not o.resolved]
        objections_note = ""
        if unresolved_objections:
            objections_note = (
                "\nNote: The following objections remain unresolved:\n"
                + "\n".join(
                    f"- {o.reason} (severity={o.severity.value})"
                    for o in unresolved_objections
                )
            )

        user_prompt = (
            f"Synthesize a final answer from the accepted claims.\n\n"
            f"Original problem: {context.problem_frame.normalized_problem if context.problem_frame else 'N/A'}\n\n"
            f"Accepted claims:\n{accepted_summary}\n"
            f"{rejected_summary}\n"
            f"{evidence_summary}\n"
            f"{objections_note}\n\n"
            f"Overall decision confidence: {decision.confidence}\n"
            "Produce the final answer."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.5,
            max_tokens=8192,
        )

        parsed = self._parse_response(response.content)
        final_answer = self._build_final_answer(
            context.run_id, parsed, decision
        )

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Final answer produced with {len(final_answer.risks)} risks "
                    f"and {len(final_answer.next_steps)} next steps.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "synthesis_complete",
            run_id=context.run_id,
            risks=len(final_answer.risks),
            next_steps=len(final_answer.next_steps),
        )

        events = [
            Event(
                id=str(uuid.uuid4()),
                event_id=f"{context.run_id}-final_answer_created",
                run_id=context.run_id,
                sequence=0,
                type=EventType.FINAL_ANSWER_CREATED,
                agent_id=self.agent_id,
                payload={"final_answer_id": final_answer.id},
            )
        ]

        return AgentResult(
            agent_id=self.agent_id,
            events=events,
            thinking_steps=thinking_steps,
            metadata={"final_answer": final_answer},
        )

    def _parse_response(self, content: str) -> dict[str, object]:
        try:
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("synthesizer_json_parse_failed", error=str(exc))
            return {
                "answer_text": content[:2000] if content else "No answer generated.",
                "rejected_alternatives": [],
                "risks": [],
                "next_steps": [],
            }

    def _build_final_answer(
        self,
        run_id: str,
        data: dict[str, object],
        decision,
    ) -> FinalAnswer:
        now = datetime.now(timezone.utc)

        risks: list[RiskItem] = []
        for risk_data in data.get("risks") or []:
            risks.append(
                RiskItem(
                    description=str(risk_data.get("description", "")),
                    severity=str(risk_data.get("severity", "medium")),
                    mitigation=str(risk_data.get("mitigation", "")) or None,
                )
            )

        return FinalAnswer(
            id=str(uuid.uuid4()),
            run_id=run_id,
            answer_text=str(data.get("answer_text", "")),
            accepted_claim_ids=decision.accepted_claim_ids,
            rejected_alternatives=[
                {
                    "claim_text": str(alt.get("claim_text", "")),
                    "reason": str(alt.get("reason", "")),
                }
                for alt in data.get("rejected_alternatives") or []
            ],
            risks=risks,
            next_steps=[
                str(s) for s in data.get("next_steps") or []
            ],
            confidence=decision.confidence,
            created_at=now,
        )
