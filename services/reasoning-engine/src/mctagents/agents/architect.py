from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    Claim,
    ClaimStatus,
    ClaimType,
    Event,
    EventType,
    ThinkingStep,
)

logger = structlog.get_logger(__name__)

PROPOSE_SYSTEM_PROMPT = """\
You are an ArchitectAgent in a claim-centered social reasoning system.

Your job is to propose 3-5 initial claims about the problem under analysis.

You MUST return valid JSON with this structure:
{
  "claims": [
    {
      "text": "string - a clear, falsifiable claim statement",
      "claim_type": "general|architecture_decision|technical_approach|risk_assessment|tradeoff_analysis|recommendation|factual|opinion",
      "confidence": 0.0-1.0,
      "requires_evidence": true/false
    }
  ]
}

Rules:
- Each claim must be independently evaluable.
- At least one claim should be a concrete recommendation.
- At least one should address risk or uncertainty.
- Confidence should reflect your actual certainty, not optimism.
- Prefer specific claims over vague ones.
- Return ONLY the JSON object.\
"""

REVISE_SYSTEM_PROMPT = """\
You are an ArchitectAgent in a claim-centered social reasoning system.

Your job is to revise existing claims that have been challenged by objections.

For each challenged claim, produce a revised version that addresses the objection.

You MUST return valid JSON with this structure:
{
  "revisions": [
    {
      "original_claim_id": "string - the UUID of the claim being revised",
      "text": "string - the revised claim statement",
      "claim_type": "same type as original",
      "confidence": 0.0-1.0,
      "reason": "string - explanation of what changed and why"
    }
  ]
}

Rules:
- Each revision must directly address the specific objection raised.
- Do not weaken claims just to avoid criticism - defend where defensible.
- If an objection is valid and the claim cannot be salvaged, create a narrower replacement.
- Maintain the same claim_type unless the revision fundamentally changes the claim's nature.
- Return ONLY the JSON object.\
"""


class ArchitectAgent(BaseAgent):
    agent_id = "architect_agent"
    role = "Architecture"
    capabilities = ["propose_claims", "revise_claims", "compare_alternatives"]

    async def act(self, context: AgentContext) -> AgentResult:
        thinking_steps: list[ThinkingStep] = []
        step_seq = 0

        problem_summary = ""
        if context.problem_frame:
            raw = context.problem_frame.original_input
            problem_summary = raw[:100] + ("..." if len(raw) > 100 else "")

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Analyzing problem: {problem_summary}",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        if context.claims:
            thinking_steps.append(ThinkingStep(
                step_type="reasoning",
                content=f"Found {len(context.claims)} existing claims. Entering revise mode.",
                agent_id=self.agent_id,
                sequence=step_seq,
            ))
            return await self._revise_claims(context, thinking_steps, step_seq + 1)

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content="No existing claims. Entering propose mode.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        return await self._propose_claims(context, thinking_steps, step_seq + 1)

    async def _propose_claims(
        self,
        context: AgentContext,
        thinking_steps: list[ThinkingStep],
        step_seq: int,
    ) -> AgentResult:
        if context.problem_frame is None:
            logger.warning("no_problem_frame", run_id=context.run_id)
            return AgentResult(agent_id=self.agent_id)

        pf = context.problem_frame
        user_prompt = (
            f"Problem: {pf.normalized_problem}\n\n"
            f"Constraints:\n"
            + "\n".join(f"- {c}" for c in pf.constraints)
            + f"\n\nRisk Level: {pf.risk_level.value}\n"
            f"Domain: {pf.domain or 'unspecified'}\n\n"
            "Propose your claims."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(PROPOSE_SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.7,
            max_tokens=4096,
        )

        parsed = self._parse_response(response.content)
        claims = self._build_claims(context.run_id, parsed)

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Proposed {len(claims)} claims.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "claims_proposed",
            run_id=context.run_id,
            count=len(claims),
        )

        events = [
            Event(
                id=str(uuid.uuid4()),
                event_id=f"{context.run_id}-claims_proposed-{c.id[:8]}",
                run_id=context.run_id,
                sequence=i,
                type=EventType.CLAIM_CREATED,
                agent_id=self.agent_id,
                payload={"claim_id": c.id, "text": c.text[:120]},
            )
            for i, c in enumerate(claims)
        ]

        return AgentResult(
            agent_id=self.agent_id,
            claims=claims,
            events=events,
            thinking_steps=thinking_steps,
        )

    async def _revise_claims(
        self,
        context: AgentContext,
        thinking_steps: list[ThinkingStep],
        step_seq: int,
    ) -> AgentResult:
        challenged = [
            c
            for c in context.claims
            if c.status in (ClaimStatus.CHALLENGED, ClaimStatus.REVISION_REQUIRED)
        ]

        if not challenged:
            return AgentResult(agent_id=self.agent_id, thinking_steps=thinking_steps)

        relevant_objections = [
            o
            for o in context.objections
            if o.target_claim_id in {c.id for c in challenged}
            and not o.resolved
        ]

        if not relevant_objections:
            return AgentResult(agent_id=self.agent_id, thinking_steps=thinking_steps)

        claims_summary = "\n".join(
            f"Claim {c.id}: {c.text} (confidence: {c.confidence})"
            for c in challenged
        )
        objections_summary = "\n".join(
            f"- Against claim {o.target_claim_id}: {o.reason} "
            f"(severity: {o.severity.value})"
            for o in relevant_objections
        )

        user_prompt = (
            "The following claims have been challenged and need revision:\n\n"
            f"Claims:\n{claims_summary}\n\n"
            f"Objections:\n{objections_summary}\n\n"
            "Propose revised claims that address each objection."
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(REVISE_SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.7,
            max_tokens=4096,
        )

        parsed = self._parse_response(response.content)
        new_claims, revision_dicts = self._build_revisions(
            context.run_id, parsed, challenged,
        )

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Revised {len(new_claims)} claims.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "claims_revised",
            run_id=context.run_id,
            count=len(new_claims),
        )

        events = [
            Event(
                id=str(uuid.uuid4()),
                event_id=f"{context.run_id}-claim_revised-{c.id[:8]}",
                run_id=context.run_id,
                sequence=i,
                type=EventType.CLAIM_REVISED,
                agent_id=self.agent_id,
                payload={"new_claim_id": c.id, "parent_claim_id": c.parent_claim_id},
            )
            for i, c in enumerate(new_claims)
        ]

        return AgentResult(
            agent_id=self.agent_id,
            claims=new_claims,
            revisions=revision_dicts,
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
            logger.warning("architect_json_parse_failed", error=str(exc))
            return {"claims": [], "revisions": []}

    def _build_claims(
        self, run_id: str, data: dict[str, object],
    ) -> list[Claim]:
        now = datetime.now(UTC)
        claims: list[Claim] = []
        for item in data.get("claims") or []:
            claim_type_str = str(item.get("claim_type", "general"))
            try:
                claim_type = ClaimType(claim_type_str)
            except ValueError:
                claim_type = ClaimType.GENERAL

            claims.append(
                Claim(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    author_agent_id=self.agent_id,
                    text=str(item.get("text", "")),
                    claim_type=claim_type,
                    confidence=float(item.get("confidence", 0.5)),
                    status=ClaimStatus.PROPOSED,
                    requires_evidence=bool(item.get("requires_evidence", False)),
                    created_at=now,
                    updated_at=now,
                ),
            )
        return claims

    def _build_revisions(
        self,
        run_id: str,
        data: dict[str, object],
        original_claims: list[Claim],
    ) -> tuple[list[Claim], list[dict[str, str]]]:
        claim_map = {c.id: c for c in original_claims}
        now = datetime.now(UTC)
        new_claims: list[Claim] = []
        revision_dicts: list[dict[str, str]] = []

        for item in data.get("revisions") or []:
            old_id = str(item.get("original_claim_id", ""))
            if old_id not in claim_map:
                continue

            original = claim_map[old_id]
            claim_type_str = str(
                item.get("claim_type", original.claim_type.value),
            )
            try:
                claim_type = ClaimType(claim_type_str)
            except ValueError:
                claim_type = original.claim_type

            new_claim = Claim(
                id=str(uuid.uuid4()),
                run_id=run_id,
                author_agent_id=self.agent_id,
                text=str(item.get("text", original.text)),
                claim_type=claim_type,
                confidence=float(item.get("confidence", original.confidence)),
                status=ClaimStatus.PROPOSED,
                requires_evidence=original.requires_evidence,
                parent_claim_id=old_id,
                created_at=now,
                updated_at=now,
            )

            new_claims.append(new_claim)
            revision_dicts.append(
                {
                    "old_claim_id": old_id,
                    "new_claim_id": new_claim.id,
                    "reason": str(item.get("reason", "Revised in response to objection")),
                },
            )

        return new_claims, revision_dicts
