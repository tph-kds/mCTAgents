"""Tests for the DebateController."""

import pytest
from mctagents.engine.debate_controller import DebateController, RoundSnapshot
from mctagents.engine.state_machine import StateMachine


@pytest.fixture
def state_machine():
    return StateMachine(max_rounds=3)


@pytest.fixture
def controller(state_machine):
    return DebateController(state_machine, {"confidence_threshold_for_acceptance": 0.7})


class TestDebateController:
    def test_initial_state(self, controller):
        assert controller.current_round == 0
        assert controller.max_rounds == 3

    def test_record_round(self, controller):
        snap = RoundSnapshot(round_number=1, claims_added=2, objections_raised=1)
        controller.record_round(snap)
        assert controller.current_round == 1

    @pytest.mark.asyncio
    async def test_should_continue_max_rounds(self, controller):
        for i in range(3):
            controller.record_round(RoundSnapshot(round_number=i + 1))
        result = await controller.should_continue({"confidence": 0.5})
        assert result is False

    @pytest.mark.asyncio
    async def test_should_continue_high_confidence(self, controller):
        controller.record_round(RoundSnapshot(round_number=1))
        result = await controller.should_continue({"confidence": 0.8})
        assert result is False

    @pytest.mark.asyncio
    async def test_should_continue_low_confidence(self, controller):
        controller.record_round(RoundSnapshot(round_number=1))
        result = await controller.should_continue({"confidence": 0.3})
        assert result is True

    @pytest.mark.asyncio
    async def test_should_continue_no_new_content(self, controller):
        controller.record_round(RoundSnapshot(round_number=1, claims_added=0, claims_revised=0, objections_raised=0))
        controller.record_round(RoundSnapshot(round_number=2, claims_added=0, claims_revised=0, objections_raised=0))
        result = await controller.should_continue({"confidence": 0.5})
        assert result is False

    @pytest.mark.asyncio
    async def test_should_continue_stable_confidence(self, controller):
        controller.record_round(RoundSnapshot(round_number=1, average_confidence=0.5, objections_raised=0))
        controller.record_round(RoundSnapshot(round_number=2, average_confidence=0.52, objections_raised=0))
        result = await controller.should_continue({"confidence": 0.52})
        assert result is False

    @pytest.mark.asyncio
    async def test_custom_policy(self, state_machine):
        controller = DebateController(state_machine, {
            "confidence_threshold_for_acceptance": 0.9,
        })
        controller.record_round(RoundSnapshot(round_number=1))
        result = await controller.should_continue({"confidence": 0.8})
        assert result is True  # 0.8 < 0.9 threshold, so continue
