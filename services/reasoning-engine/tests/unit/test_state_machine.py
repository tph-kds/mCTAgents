"""Tests for the CCSR state machine."""

import pytest

from mctagents.engine.state_machine import (
    InvalidTransitionError,
    RunPhase,
    StateMachine,
)


class TestStateMachine:
    def test_initial_state(self):
        sm = StateMachine()
        assert sm.phase == RunPhase.QUEUED

    def test_valid_happy_path(self):
        sm = StateMachine()
        sm.transition("start")
        assert sm.phase == RunPhase.FRAMING
        sm.transition("problem_framed")
        assert sm.phase == RunPhase.SOCIETY_PLANNING
        sm.transition("society_selected")
        assert sm.phase == RunPhase.CLAIM_PROPOSAL
        sm.transition("claims_proposed")
        assert sm.phase == RunPhase.EVIDENCE_ATTACHMENT
        sm.transition("evidence_attached")
        assert sm.phase == RunPhase.CRITICISM
        sm.transition("criticism_complete")
        assert sm.phase == RunPhase.REVISION
        sm.transition("revision_complete")
        assert sm.phase == RunPhase.JUDGING
        sm.transition("judge_accepted")
        assert sm.phase == RunPhase.SYNTHESIS
        sm.transition("synthesis_complete")
        assert sm.phase == RunPhase.COMPLETED

    def test_invalid_transition_raises(self):
        sm = StateMachine()
        with pytest.raises(InvalidTransitionError) as exc_info:
            sm.transition("claims_proposed")
        assert exc_info.value.current == RunPhase.QUEUED
        assert exc_info.value.event == "claims_proposed"

    def test_can_transition(self):
        sm = StateMachine()
        assert sm.can_transition("start") is True
        assert sm.can_transition("cancel") is True
        assert sm.can_transition("claims_proposed") is False

    def test_cancel_from_any_active_phase(self):
        for phase_event in [
            ("start",),
            ("start", "problem_framed"),
            ("start", "problem_framed", "society_selected"),
        ]:
            sm = StateMachine()
            for event in phase_event:
                sm.transition(event)
            assert sm.can_transition("cancel") is True
            sm.transition("cancel")
            assert sm.phase == RunPhase.CANCELLED

    def test_escalation_loop(self):
        sm = StateMachine()
        # Navigate to JUDGING
        for event in [
            "start", "problem_framed", "society_selected",
            "claims_proposed", "evidence_attached", "criticism_complete",
            "revision_complete",
        ]:
            sm.transition(event)
        assert sm.phase == RunPhase.JUDGING

        # Judge says needs more debate
        sm.transition("needs_more_debate")
        assert sm.phase == RunPhase.ESCALATION

        # Escalation resolves back to CLAIM_PROPOSAL
        sm.transition("escalation_resolved")
        assert sm.phase == RunPhase.CLAIM_PROPOSAL

    def test_history_tracking(self):
        sm = StateMachine()
        sm.transition("start")
        sm.transition("problem_framed")
        assert len(sm.history) == 2
        assert sm.history[0] == (RunPhase.QUEUED, "start", RunPhase.FRAMING)
        assert sm.history[1] == (RunPhase.FRAMING, "problem_framed", RunPhase.SOCIETY_PLANNING)

    def test_max_rounds(self):
        sm = StateMachine(max_rounds=5)
        assert sm.max_rounds == 5

    def test_should_escalate(self):
        sm = StateMachine()
        assert sm.should_escalate(0.3) is True
        assert sm.should_escalate(0.5) is False
        assert sm.should_escalate(0.8, threshold=0.7) is False
