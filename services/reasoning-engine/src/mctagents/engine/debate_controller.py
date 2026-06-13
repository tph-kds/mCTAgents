from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from mctagents.engine.state_machine import StateMachine

logger = structlog.get_logger(__name__)


@dataclass
class RoundSnapshot:
    """A record of what happened in one debate round."""

    round_number: int
    claims_added: int = 0
    claims_revised: int = 0
    objections_raised: int = 0
    evidence_added: int = 0
    average_confidence: float = 0.0


class DebateController:
    """Decides whether to continue or stop the debate loop."""

    def __init__(self, state_machine: StateMachine, policy: dict | None = None) -> None:
        self._state = state_machine
        self._policy = policy or {}
        self._round_history: list[RoundSnapshot] = []

    @property
    def max_rounds(self) -> int:
        return self._state.max_rounds

    @property
    def current_round(self) -> int:
        return len(self._round_history)

    def record_round(self, snapshot: RoundSnapshot) -> None:
        self._round_history.append(snapshot)
        logger.info(
            "debate_round_recorded",
            round=snapshot.round_number,
            claims_added=snapshot.claims_added,
            objections=snapshot.objections_raised,
            avg_confidence=snapshot.average_confidence,
        )

    async def should_continue(self, context: dict) -> bool:
        if self.current_round >= self.max_rounds:
            logger.info(
                "debate_stop_max_rounds",
                current=self.current_round,
                max=self.max_rounds,
            )
            return False

        confidence = float(context.get("confidence", 0.0))
        acceptance_threshold = float(
            self._policy.get("confidence_threshold_for_acceptance", 0.7)
        )
        if confidence >= acceptance_threshold:
            logger.info(
                "debate_stop_high_confidence",
                confidence=confidence,
                threshold=acceptance_threshold,
            )
            return False

        if self._has_low_marginal_value():
            logger.info(
                "debate_stop_low_marginal_value",
                round=self.current_round,
            )
            return False

        escalation_threshold = float(
            self._policy.get("escalation_threshold", 0.5)
        )
        if confidence < escalation_threshold and self.current_round < self.max_rounds:
            logger.info(
                "debate_continue_low_confidence",
                confidence=confidence,
                remaining=self.max_rounds - self.current_round,
            )
            return True

        logger.info(
            "debate_continue_default",
            confidence=confidence,
            round=self.current_round,
        )
        return True

    def _has_low_marginal_value(self) -> bool:
        if len(self._round_history) < 2:
            return False

        last_two = self._round_history[-2:]
        no_new_content = all(
            snap.claims_added == 0
            and snap.claims_revised == 0
            and snap.objections_raised == 0
            for snap in last_two
        )

        if no_new_content:
            return True

        if len(last_two) == 2:
            delta = abs(
                last_two[1].average_confidence - last_two[0].average_confidence
            )
            if delta < 0.05 and last_two[1].objections_raised == 0:
                return True

        return False
