"""Tests for the EventService."""

import pytest
from mctagents.core.protocol import Event, EventType
from mctagents.services.event_service import EventService


@pytest.fixture
def event_service():
    return EventService()


class TestEventService:
    @pytest.mark.asyncio
    async def test_emit_creates_event(self, event_service):
        event = await event_service.emit("run1", EventType.RUN_STARTED, {"problem": "test"})
        assert event.run_id == "run1"
        assert event.type == EventType.RUN_STARTED
        assert event.sequence == 1

    @pytest.mark.asyncio
    async def test_emit_increments_sequence(self, event_service):
        e1 = await event_service.emit("run1", EventType.RUN_STARTED, {})
        e2 = await event_service.emit("run1", EventType.AGENT_STARTED, {})
        assert e2.sequence == 2

    @pytest.mark.asyncio
    async def test_get_events_returns_all(self, event_service):
        await event_service.emit("run1", EventType.RUN_STARTED, {})
        await event_service.emit("run1", EventType.RUN_COMPLETED, {})
        events = event_service.get_events("run1")
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_subscribe_receives_events(self, event_service):
        queue = event_service.subscribe("run1")
        await event_service.emit("run1", EventType.RUN_STARTED, {"problem": "x"})
        assert not queue.empty()
        event = queue.get_nowait()
        assert event.type == EventType.RUN_STARTED

    @pytest.mark.asyncio
    async def test_unsubscribe(self, event_service):
        queue = event_service.subscribe("run1")
        event_service.unsubscribe("run1", queue)
        await event_service.emit("run1", EventType.RUN_STARTED, {})
        assert queue.empty()

    @pytest.mark.asyncio
    async def test_clear_run(self, event_service):
        await event_service.emit("run1", EventType.RUN_STARTED, {})
        event_service.clear_run("run1")
        assert event_service.get_events("run1") == []

    @pytest.mark.asyncio
    async def test_get_event_count(self, event_service):
        await event_service.emit("run1", EventType.RUN_STARTED, {})
        await event_service.emit("run1", EventType.RUN_COMPLETED, {})
        assert event_service.get_event_count("run1") == 2

    @pytest.mark.asyncio
    async def test_emit_with_valid_event_type(self, event_service):
        event = await event_service.emit("run1", EventType.AGENT_ERROR, {"key": "value"})
        assert event.type == EventType.AGENT_ERROR
