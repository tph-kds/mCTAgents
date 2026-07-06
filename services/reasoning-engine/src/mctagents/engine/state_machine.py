from __future__ import annotations

from enum import StrEnum

import structlog

logger = structlog.get_logger(__name__)


class RunPhase(StrEnum):
    QUEUED = "queued"
    FRAMING = "framing"
    SOCIETY_PLANNING = "society_planning"
    CLAIM_PROPOSAL = "claim_proposal"
    EVIDENCE_ATTACHMENT = "evidence_attachment"
    CRITICISM = "criticism"
    REVISION = "revision"
    JUDGING = "judging"
    ESCALATION = "escalation"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidTransitionError(Exception):
    """Raised when a state machine transition is not valid."""

    def __init__(self, current: RunPhase, event: str) -> None:
        self.current = current
        self.event = event
        super().__init__(
            f"Invalid transition: {current.value} + '{event}'",
        )


class StateMachine:
    """Deterministic state machine for the CCSR workflow phases."""

    VALID_TRANSITIONS: dict[tuple[RunPhase, str], RunPhase] = {
        (RunPhase.QUEUED, "start"): RunPhase.FRAMING,
        (RunPhase.FRAMING, "problem_framed"): RunPhase.SOCIETY_PLANNING,
        (RunPhase.SOCIETY_PLANNING, "society_selected"): RunPhase.CLAIM_PROPOSAL,
        (RunPhase.CLAIM_PROPOSAL, "claims_proposed"): RunPhase.EVIDENCE_ATTACHMENT,
        (RunPhase.EVIDENCE_ATTACHMENT, "evidence_attached"): RunPhase.CRITICISM,
        (RunPhase.CRITICISM, "criticism_complete"): RunPhase.REVISION,
        (RunPhase.REVISION, "revision_complete"): RunPhase.JUDGING,
        (RunPhase.JUDGING, "judge_accepted"): RunPhase.SYNTHESIS,
        (RunPhase.JUDGING, "needs_more_debate"): RunPhase.ESCALATION,
        (RunPhase.ESCALATION, "escalation_resolved"): RunPhase.CLAIM_PROPOSAL,
        (RunPhase.SYNTHESIS, "synthesis_complete"): RunPhase.COMPLETED,
        (RunPhase.QUEUED, "cancel"): RunPhase.CANCELLED,
        (RunPhase.FRAMING, "cancel"): RunPhase.CANCELLED,
        (RunPhase.SOCIETY_PLANNING, "cancel"): RunPhase.CANCELLED,
        (RunPhase.CLAIM_PROPOSAL, "cancel"): RunPhase.CANCELLED,
        (RunPhase.EVIDENCE_ATTACHMENT, "cancel"): RunPhase.CANCELLED,
        (RunPhase.CRITICISM, "cancel"): RunPhase.CANCELLED,
        (RunPhase.REVISION, "cancel"): RunPhase.CANCELLED,
        (RunPhase.JUDGING, "cancel"): RunPhase.CANCELLED,
        (RunPhase.ESCALATION, "cancel"): RunPhase.CANCELLED,
        (RunPhase.SYNTHESIS, "cancel"): RunPhase.CANCELLED,
    }

    def __init__(self, max_rounds: int = 3) -> None:
        self._phase: RunPhase = RunPhase.QUEUED
        self._max_rounds = max_rounds
        self._history: list[tuple[RunPhase, str, RunPhase]] = []

    @property
    def phase(self) -> RunPhase:
        return self._phase

    @property
    def max_rounds(self) -> int:
        return self._max_rounds

    @property
    def history(self) -> list[tuple[RunPhase, str, RunPhase]]:
        return list(self._history)

    def transition(self, event: str) -> RunPhase:
        key = (self._phase, event)
        if key not in self.VALID_TRANSITIONS:
            raise InvalidTransitionError(self._phase, event)

        old = self._phase
        self._phase = self.VALID_TRANSITIONS[key]
        self._history.append((old, event, self._phase))

        logger.info(
            "state_transition",
            from_phase=old.value,
            transition_event=event,
            to_phase=self._phase.value,
        )
        return self._phase

    def can_transition(self, event: str) -> bool:
        return (self._phase, event) in self.VALID_TRANSITIONS

    def should_escalate(
        self, confidence: float, threshold: float = 0.5,
    ) -> bool:
        return confidence < threshold
