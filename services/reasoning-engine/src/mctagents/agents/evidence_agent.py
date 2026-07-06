from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    ClaimStatus,
    Evidence,
    EventType,
    SourceType,
    ThinkingStep,
)

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are an EvidenceAgent in a claim-centered social reasoning system.

Your job is to evaluate claims and assess what evidence exists or is needed.

You MUST return valid JSON with this structure:
{
  "assessments": [
    {
      "claim_id": "string - UUID of the claim",
      "has_sufficient_evidence": true/false,
      "evidence_summary": "string - summary of available evidence (if any)",
      "evidence_quality": 0.0-1.0,
      "missing_evidence": "string - description of what evidence is still needed",
      "source_type": "internal_memory|uploaded_document|web_source|official_documentation|academic_paper|code_execution_result",
      "recommended_action": "accept_evidence|request_more_evidence|flag_unsupported"
    }
  ]
}

Rules:
- Be honest about evidence quality. Do not inflate reliability scores.
- If no external evidence exists, say so clearly.
- For factual claims, demand stronger evidence than for opinion claims.
- Distinguish between "no evidence found" and "evidence exists but is weak".
- Return ONLY the JSON object.\
"""


class EvidenceAgent(BaseAgent):
    agent_id = "evidence_agent"
    role = "Evidence"
    capabilities = ["retrieve_evidence", "score_reliability", "label_unsupported"]

    def __init__(self, model_provider, evidence_service=None):
        super().__init__(model_provider)
        self._evidence_service = evidence_service

    async def act(self, context: AgentContext) -> AgentResult:
        thinking_steps: list[ThinkingStep] = []
        step_seq = 0

        unsupported = [
            c
            for c in context.claims
            if c.requires_evidence
            and c.evidence_status.value
            in (ClaimStatus.PROPOSED.value, ClaimStatus.EVIDENCE_REQUESTED.value)
            and c.status
            not in (
                ClaimStatus.REJECTED.value,
                ClaimStatus.UNCERTAIN.value,
            )
        ]

        if not unsupported:
            return AgentResult(agent_id=self.agent_id)

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Evaluating evidence requirements for {len(unsupported)} claims.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        thinking_steps.append(ThinkingStep(
            step_type="tool_call",
            content="Searching for relevant evidence...",
            agent_id=self.agent_id,
            tool_name="evidence_service",
            tool_args={"claim_count": len(unsupported)},
            sequence=step_seq,
        ))
        step_seq += 1

        claims_summary = "\n".join(
            f"Claim {c.id} (type={c.claim_type.value}, confidence={c.confidence}): "
            f"{c.text}"
            for c in unsupported
        )

        pf_summary = ""
        if context.problem_frame:
            pf_summary = (
                f"Problem domain: {context.problem_frame.domain or 'unspecified'}\n"
                f"Risk level: {context.problem_frame.risk_level.value}\n"
            )

        user_prompt = (
            f"{pf_summary}\n"
            f"Claims requiring evidence assessment:\n{claims_summary}\n\n"
            f"Existing evidence in context: {len(context.evidence)} items\n\n"
            "Assess the evidence situation for each claim."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.4,
            max_tokens=4096,
        )

        parsed = self._parse_response(response.content)
        evidence_items, events = self._build_evidence(
            context.run_id, parsed, unsupported
        )

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Assessed {len(unsupported)} claims, produced {len(evidence_items)} evidence items.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "evidence_assessed",
            run_id=context.run_id,
            claims_assessed=len(unsupported),
            evidence_items=len(evidence_items),
        )

        return AgentResult(
            agent_id=self.agent_id,
            evidence=evidence_items,
            events=events,
            thinking_steps=thinking_steps,
        )

    def _parse_response(self, content: str) -> dict[str, object]:
        try:
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("evidence_json_parse_failed", error=str(exc))
            return {"assessments": []}

    def _build_evidence(
        self,
        run_id: str,
        data: dict[str, object],
        claims: list,
    ) -> tuple[list[Evidence], list[Event]]:
        now = datetime.now(timezone.utc)
        evidence_items: list[Evidence] = []
        events: list[Event] = []

        for assessment in data.get("assessments") or []:
            claim_id = str(assessment.get("claim_id", ""))
            summary = str(assessment.get("evidence_summary", ""))
            quality = float(assessment.get("evidence_quality", 0.5))
            source_str = str(
                assessment.get("source_type", "internal_memory")
            )
            try:
                source_type = SourceType(source_str)
            except ValueError:
                source_type = SourceType.INTERNAL_MEMORY

            if not summary:
                continue

            evidence = Evidence(
                id=str(uuid.uuid4()),
                run_id=run_id,
                source_type=source_type,
                summary=summary,
                reliability_score=quality,
                supports_claim_ids=[claim_id] if claim_id else [],
                created_at=now,
            )

            evidence_items.append(evidence)
            events.append(
                Event(
                    id=str(uuid.uuid4()),
                    event_id=f"{run_id}-evidence-{evidence.id[:8]}",
                    run_id=run_id,
                    sequence=len(evidence_items),
                    type=EventType.EVIDENCE_ATTACHED,
                    agent_id=self.agent_id,
                    payload={
                        "evidence_id": evidence.id,
                        "claim_id": claim_id,
                        "quality": quality,
                    },
                )
            )

        return evidence_items, events
