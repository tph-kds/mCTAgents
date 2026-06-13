from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    ClaimStatus,
    EventType,
    Objection,
    Severity,
)

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a CriticAgent in a claim-centered social reasoning system.

Your job is to find genuine weaknesses, gaps, and contradictions in claims.
You are adversarial but fair - your goal is to improve reasoning quality.

You MUST return valid JSON with this structure:
{
  "objections": [
    {
      "target_claim_id": "string - UUID of the claim being challenged",
      "reason": "string - detailed explanation of the weakness or gap",
      "severity": "low|medium|high|critical",
      "requested_fix": "string or null - suggested way to resolve the objection"
    }
  ]
}

Rules:
- Only raise genuine objections, not nitpicks. Every objection must have substance.
- Check for: logical gaps, unsupported assumptions, missing evidence, contradictions with other claims, feasibility issues, overlooked risks.
- Do NOT manufacture objections just to be adversarial.
- If a claim is solid, return an empty objections list rather than forcing criticism.
- Severity must reflect actual impact on the claim's validity.
- Return ONLY the JSON object.\
"""


class CriticAgent(BaseAgent):
    agent_id = "critic_agent"
    role = "Criticism"
    capabilities = ["challenge_claims", "detect_contradictions", "identify_gaps"]

    async def act(self, context: AgentContext) -> AgentResult:
        if not context.claims:
            return AgentResult(agent_id=self.agent_id)

        claims_summary = "\n".join(
            f"Claim {c.id} (type={c.claim_type.value}, confidence={c.confidence}, "
            f"status={c.status.value}): {c.text}"
            for c in context.claims
            if c.status
            not in (ClaimStatus.REJECTED.value, ClaimStatus.UNCERTAIN.value)
        )

        if not claims_summary:
            return AgentResult(agent_id=self.agent_id)

        evidence_summary = ""
        if context.evidence:
            evidence_summary = "\nAvailable evidence:\n" + "\n".join(
                f"- Evidence {e.id} (reliability={e.reliability_score}): "
                f"{e.summary} (supports: {e.supports_claim_ids})"
                for e in context.evidence
            )

        existing_objections = ""
        if context.objections:
            existing_objections = "\nPreviously raised objections:\n" + "\n".join(
                f"- Against {o.target_claim_id}: {o.reason} (severity={o.severity.value})"
                for o in context.objections
            )

        user_prompt = (
            "Analyze the following claims for weaknesses and gaps.\n\n"
            f"Claims:\n{claims_summary}\n"
            f"{evidence_summary}\n"
            f"{existing_objections}\n\n"
            "Find genuine problems. Do not fabricate objections."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.6,
            max_tokens=4096,
        )

        parsed = self._parse_response(response.content)
        objections, events = self._build_objections(
            context.run_id, parsed
        )

        logger.info(
            "criticism_complete",
            run_id=context.run_id,
            objections_raised=len(objections),
        )

        return AgentResult(
            agent_id=self.agent_id,
            objections=objections,
            events=events,
        )

    def _parse_response(self, content: str) -> dict[str, object]:
        try:
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("critic_json_parse_failed", error=str(exc))
            return {"objections": []}

    def _build_objections(
        self, run_id: str, data: dict[str, object]
    ) -> tuple[list[Objection], list[Event]]:
        now = datetime.now(timezone.utc)
        objections: list[Objection] = []
        events: list[Event] = []

        for item in data.get("objections") or []:
            severity_str = str(item.get("severity", "medium")).lower()
            try:
                severity = Severity(severity_str)
            except ValueError:
                severity = Severity.MEDIUM

            objection = Objection(
                id=str(uuid.uuid4()),
                run_id=run_id,
                target_claim_id=str(item.get("target_claim_id", "")),
                author_agent_id=self.agent_id,
                reason=str(item.get("reason", "")),
                severity=severity,
                requested_fix=str(item.get("requested_fix", "")) or None,
                created_at=now,
            )

            objections.append(objection)
            events.append(
                Event(
                    id=str(uuid.uuid4()),
                    event_id=f"{run_id}-objection-{objection.id[:8]}",
                    run_id=run_id,
                    sequence=len(objections),
                    type=EventType.OBJECTION_CREATED,
                    agent_id=self.agent_id,
                    payload={
                        "objection_id": objection.id,
                        "target_claim_id": objection.target_claim_id,
                        "severity": severity.value,
                    },
                )
            )

        return objections, events
