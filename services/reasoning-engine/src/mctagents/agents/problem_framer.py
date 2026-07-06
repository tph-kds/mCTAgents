from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog

from mctagents.agents.base import AgentContext, AgentResult, BaseAgent
from mctagents.core.protocol import (
    Claim,
    Event,
    EventType,
    ProblemFrame,
    RiskLevel,
    ThinkingStep,
)

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a ProblemFramer agent in a claim-centered social reasoning system.

Your job is to analyze the user's raw input and produce a structured problem frame.

You MUST return valid JSON with exactly these fields:
{
  "normalized_problem": "string - cleaned, precise problem statement",
  "constraints": ["string - list of hard constraints"],
  "success_criteria": ["string - measurable success criteria"],
  "risk_level": "low|medium|high|critical",
  "domain": "string or null - detected domain (e.g. software, finance, legal)",
  "requires_business_decision": true/false,
  "requires_research": true/false,
  "requires_code": true/false
}

Rules:
- Be precise and factual. Do not invent constraints that are not implied by the input.
- Risk level must reflect actual severity of getting the answer wrong.
- If ambiguous, flag it in success_criteria rather than guessing.
- Return ONLY the JSON object, no preamble.\
"""


class ProblemFramer(BaseAgent):
    agent_id = "problem_framer"
    role = "Framing"
    capabilities = ["normalize", "detect_domain", "set_risk"]

    async def act(self, context: AgentContext) -> AgentResult:
        thinking_steps: list[ThinkingStep] = []
        step_seq = 0

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content="Normalizing user input into structured problem frame.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        original_input = ""
        if context.problem_frame is not None:
            original_input = context.problem_frame.original_input

        user_prompt = (
            f"Analyze the following input and create a structured problem frame:\n\n"
            f"---\n{original_input}\n---"
        )

        response = await self._model_provider.chat(
            messages=self._build_messages(SYSTEM_PROMPT, user_prompt),
            json_mode=True,
            temperature=0.3,
            max_tokens=2048,
        )

        parsed = self._parse_response(response.content)
        problem_frame = self._build_problem_frame(context.run_id, parsed)

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Framed problem as {problem_frame.risk_level.value} risk, "
                    f"domain={problem_frame.domain or 'unspecified'}.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))

        logger.info(
            "problem_framed",
            run_id=context.run_id,
            risk_level=problem_frame.risk_level,
            domain=problem_frame.domain,
        )

        return AgentResult(
            agent_id=self.agent_id,
            thinking_steps=thinking_steps,
            events=[
                Event(
                    id=str(uuid.uuid4()),
                    event_id=f"{context.run_id}-problem_framed",
                    run_id=context.run_id,
                    sequence=0,
                    type=EventType.PROBLEM_FRAMED,
                    agent_id=self.agent_id,
                    payload={"problem_frame_id": problem_frame.id},
                )
            ],
            metadata={"problem_frame": problem_frame},
        )

    def _parse_response(self, content: str) -> dict[str, object]:
        try:
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("framer_json_parse_failed", error=str(exc))
            return {
                "normalized_problem": content[:500],
                "constraints": [],
                "success_criteria": [],
                "risk_level": "medium",
                "domain": None,
                "requires_business_decision": False,
                "requires_research": False,
                "requires_code": False,
            }

    def _build_problem_frame(
        self, run_id: str, data: dict[str, object]
    ) -> ProblemFrame:
        risk_str = str(data.get("risk_level", "medium")).lower()
        try:
            risk_level = RiskLevel(risk_str)
        except ValueError:
            risk_level = RiskLevel.MEDIUM

        return ProblemFrame(
            id=str(uuid.uuid4()),
            run_id=run_id,
            original_input=data.get("normalized_problem", "") or "",
            normalized_problem=str(data.get("normalized_problem", "")),
            constraints=[str(c) for c in (data.get("constraints") or [])],
            success_criteria=[
                str(c) for c in (data.get("success_criteria") or [])
            ],
            risk_level=risk_level,
            domain=str(data.get("domain", "")) or None,
            requires_business_decision=bool(
                data.get("requires_business_decision", False)
            ),
            requires_research=bool(data.get("requires_research", False)),
            requires_code=bool(data.get("requires_code", False)),
            created_at=datetime.now(timezone.utc),
        )
