from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Protocol

import structlog

from mctagents.agents.architect import ArchitectAgent
from mctagents.agents.base import AgentContext, AgentResult
from mctagents.agents.critic import CriticAgent
from mctagents.agents.evidence_agent import EvidenceAgent
from mctagents.agents.judge import JudgeAgent
from mctagents.agents.problem_framer import ProblemFramer
from mctagents.agents.synthesizer import SynthesizerAgent
from mctagents.core.protocol import (
    Claim,
    ClaimStatus,
    Decision,
    Event,
    EventType,
    Evidence,
    FinalAnswer,
    Objection,
    ProblemFrame,
    Revision,
)
from mctagents.engine.debate_controller import DebateController, RoundSnapshot
from mctagents.engine.state_machine import (
    InvalidTransitionError,
    RunPhase,
    StateMachine,
)

logger = structlog.get_logger(__name__)


class EventPublisher(Protocol):
    async def publish(self, event) -> None: ...


class StorageService(Protocol):
    async def save_claim(self, claim: Claim) -> None: ...
    async def save_evidence(self, evidence: Evidence) -> None: ...
    async def save_objection(self, objection: Objection) -> None: ...
    async def save_revision(self, revision: Revision) -> None: ...
    async def save_decision(self, decision: Decision) -> None: ...
    async def save_final_answer(self, answer: FinalAnswer) -> None: ...
    async def save_problem_frame(self, frame: ProblemFrame) -> None: ...
    async def save_event(self, event) -> None: ...


class ReasoningEngine:
    """Main orchestrator for the CCSR reasoning workflow."""

    def __init__(
        self,
        model_router,
        event_service: EventPublisher | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        provider = model_router.providers.get("ollama")
        if provider is None:
            raise ValueError("ModelRouter must have an 'ollama' provider")

        self.framer = ProblemFramer(provider)
        self.architect = ArchitectAgent(provider)
        self.evidence_agent = EvidenceAgent(provider)
        self.critic = CriticAgent(provider)
        self.judge = JudgeAgent(provider)
        self.synthesizer = SynthesizerAgent(provider)

        self._event_service = event_service
        self._storage = storage_service

    async def run(
        self,
        run_id: str,
        problem: str,
        policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        policy = policy or {}
        max_rounds = int(policy.get("max_rounds", 2))

        state = StateMachine(max_rounds=max_rounds)
        debate = DebateController(state, policy)

        context = AgentContext(
            run_id=run_id,
            problem_frame=ProblemFrame(
                id=str(uuid.uuid4()),
                run_id=run_id,
                original_input=problem,
                normalized_problem=problem,
            ),
        )

        await self._emit(
            run_id, EventType.RUN_STARTED, {"problem": problem[:500], "policy": policy},
        )

        try:
            await self._phase_framing(state, context)
            await self._phase_society_planning(state, context)
            await self._phase_evidence(state, context)

            debate_round = 0
            while True:
                debate_round += 1
                context.debate_round = debate_round

                await self._phase_claim_proposal(state, context)
                await self._phase_evidence(state, context)
                await self._phase_criticism(state, context)
                await self._phase_revision(state, context)
                decision = await self._phase_judging(state, context)

                if decision is None:
                    break

                snapshot = self._make_snapshot(
                    debate_round, context, decision,
                )
                debate.record_round(snapshot)

                should_continue = await debate.should_continue(
                    {"confidence": decision.confidence},
                )

                if not should_continue or not decision.needs_more_debate:
                    break

                state.transition("needs_more_debate")
                logger.info(
                    "escalation_loop",
                    run_id=run_id,
                    round=debate_round,
                    confidence=decision.confidence,
                )

            await self._phase_synthesis(state, context)

            await self._emit(
                run_id,
                EventType.RUN_COMPLETED,
                {"total_rounds": debate_round},
            )

            return self._build_result(context)

        except Exception as exc:
            logger.error("run_failed", run_id=run_id, error=str(exc))
            try:
                state.transition("cancel")
            except InvalidTransitionError:
                self._force_failed(state)
            await self._emit(run_id, EventType.RUN_FAILED, {"error": str(exc)})
            raise

    async def _phase_framing(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        state.transition("start")
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.framer.agent_id, "phase": "framing"},
        )

        result = await self.framer.act(context)
        await self._process_result(context, result)

        pf = result.metadata.get("problem_frame")
        if pf is not None:
            context.problem_frame = pf
            if self._storage:
                await self._storage.save_problem_frame(pf)

        state.transition("problem_framed")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.framer.agent_id, "phase": "framing"},
        )

    async def _phase_society_planning(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        state.transition("problem_framed")
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": "society_planner", "phase": "society_planning"},
        )

        state.transition("society_selected")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": "society_planner", "phase": "society_planning"},
        )

    async def _phase_claim_proposal(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        current_phase = state.phase
        if current_phase == RunPhase.ESCALATION:
            state.transition("escalation_resolved")
        elif current_phase == RunPhase.QUEUED:
            state.transition("start")
            state.transition("problem_framed")
            state.transition("society_selected")

        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.architect.agent_id, "phase": "claim_proposal"},
        )

        result = await self.architect.act(context)
        await self._process_result(context, result)

        for claim in result.claims:
            context.claims.append(claim)
            if self._storage:
                await self._storage.save_claim(claim)

        for rev_dict in result.revisions:
            old_id = rev_dict.get("old_claim_id", "")
            new_id = rev_dict.get("new_claim_id", "")
            revision = Revision(
                id=str(uuid.uuid4()),
                run_id=context.run_id,
                old_claim_id=old_id,
                new_claim_id=new_id,
                reason=rev_dict.get("reason", ""),
            )
            context.revisions.append(rev_dict)
            if self._storage:
                await self._storage.save_revision(revision)

        state.transition("claims_proposed")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.architect.agent_id, "phase": "claim_proposal"},
        )

    async def _phase_evidence(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        if state.phase == RunPhase.EVIDENCE_ATTACHMENT:
            pass
        else:
            state.transition("claims_proposed") if state.can_transition(
                "claims_proposed",
            ) else None

        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.evidence_agent.agent_id, "phase": "evidence_attachment"},
        )

        result = await self.evidence_agent.act(context)
        await self._process_result(context, result)

        for ev in result.evidence:
            context.evidence.append(ev)
            if self._storage:
                await self._storage.save_evidence(ev)

        if state.can_transition("evidence_attached"):
            state.transition("evidence_attached")

        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.evidence_agent.agent_id, "phase": "evidence_attachment"},
        )

    async def _phase_criticism(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.critic.agent_id, "phase": "criticism"},
        )

        result = await self.critic.act(context)
        await self._process_result(context, result)

        for obj in result.objections:
            context.objections.append(obj)
            if self._storage:
                await self._storage.save_objection(obj)

            for claim in context.claims:
                if claim.id == obj.target_claim_id:
                    claim.status = ClaimStatus.CHALLENGED
                    claim.updated_at = datetime.now(UTC)

        state.transition("criticism_complete")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.critic.agent_id, "phase": "criticism"},
        )

    async def _phase_revision(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.architect.agent_id, "phase": "revision"},
        )

        result = await self.architect.act(context)
        await self._process_result(context, result)

        for claim in result.claims:
            context.claims.append(claim)
            if self._storage:
                await self._storage.save_claim(claim)

        for rev_dict in result.revisions:
            old_id = rev_dict.get("old_claim_id", "")
            new_id = rev_dict.get("new_claim_id", "")
            revision = Revision(
                id=str(uuid.uuid4()),
                run_id=context.run_id,
                old_claim_id=old_id,
                new_claim_id=new_id,
                reason=rev_dict.get("reason", ""),
            )
            context.revisions.append(rev_dict)
            if self._storage:
                await self._storage.save_revision(revision)

        state.transition("revision_complete")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.architect.agent_id, "phase": "revision"},
        )

    async def _phase_judging(
        self, state: StateMachine, context: AgentContext,
    ) -> Decision | None:
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.judge.agent_id, "phase": "judging"},
        )

        result = await self.judge.act(context)
        await self._process_result(context, result)

        decision = result.metadata.get("decision")
        if decision is None:
            state.transition("judge_accepted")
            await self._emit(
                context.run_id,
                EventType.AGENT_COMPLETED,
                {"agent": self.judge.agent_id, "phase": "judging"},
            )
            return None

        if self._storage:
            await self._storage.save_decision(decision)

        for claim in context.claims:
            if claim.id in decision.accepted_claim_ids:
                claim.status = ClaimStatus.ACCEPTED
            elif claim.id in decision.rejected_claim_ids:
                claim.status = ClaimStatus.REJECTED
                claim.rejection_reason = decision.score_breakdown.get(
                    claim.id, {},
                ).get("rejection_reason")
            elif claim.id in decision.uncertain_claim_ids:
                claim.status = ClaimStatus.UNCERTAIN
            claim.updated_at = datetime.now(UTC)
            if self._storage:
                await self._storage.save_claim(claim)

        if decision.needs_more_debate:
            state.transition("needs_more_debate")
        else:
            state.transition("judge_accepted")

        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {
                "agent": self.judge.agent_id,
                "phase": "judging",
                "accepted": len(decision.accepted_claim_ids),
                "rejected": len(decision.rejected_claim_ids),
            },
        )

        return decision

    async def _phase_synthesis(
        self, state: StateMachine, context: AgentContext,
    ) -> None:
        await self._emit(
            context.run_id,
            EventType.AGENT_STARTED,
            {"agent": self.synthesizer.agent_id, "phase": "synthesis"},
        )

        result = await self.synthesizer.act(context)
        await self._process_result(context, result)

        final_answer = result.metadata.get("final_answer")
        if final_answer is not None:
            if self._storage:
                await self._storage.save_final_answer(final_answer)
            context.metadata["final_answer"] = final_answer

        state.transition("synthesis_complete")
        await self._emit(
            context.run_id,
            EventType.AGENT_COMPLETED,
            {"agent": self.synthesizer.agent_id, "phase": "synthesis"},
        )

    async def _process_result(
        self, context: AgentContext, result: AgentResult,
    ) -> None:
        for event in result.events:
            if self._event_service:
                await self._event_service.publish(event)
            if self._storage:
                await self._storage.save_event(event)

    async def _emit(
        self,
        run_id: str,
        event_type: EventType,
        payload: dict[str, Any],
    ) -> None:
        event = Event(
            id=str(uuid.uuid4()),
            event_id=f"{run_id}-{event_type.value}-{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            sequence=0,
            type=event_type,
            payload=payload,
        )
        if self._event_service:
            await self._event_service.publish(event)
        if self._storage:
            await self._storage.save_event(event)

    def _make_snapshot(
        self,
        round_num: int,
        context: AgentContext,
        decision: Decision,
    ) -> RoundSnapshot:
        return RoundSnapshot(
            round_number=round_num,
            claims_added=len(context.claims),
            claims_revised=len(context.revisions),
            objections_raised=len(context.objections),
            evidence_added=len(context.evidence),
            average_confidence=decision.confidence,
        )

    def _build_result(self, context: AgentContext) -> dict[str, Any]:
        final_answer = context.metadata.get("final_answer")
        return {
            "run_id": context.run_id,
            "status": "completed",
            "claims": [c.model_dump() for c in context.claims],
            "evidence": [e.model_dump() for e in context.evidence],
            "objections": [o.model_dump() for o in context.objections],
            "revisions": context.revisions,
            "final_answer": final_answer.model_dump() if final_answer else None,
        }

    def _force_failed(self, state: StateMachine) -> None:
        object.__setattr__(state, "_phase", RunPhase.FAILED)
