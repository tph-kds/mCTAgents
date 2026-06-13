"""Tests for the EventService."""

import asyncio
import pytest
from mctagents.core.protocol import Event, EventType
from mctagents.services.event_service import EventService


@pytest.fixture
def event_service():
    return EventService()


class TestEventService:
    def test_emit_creates_event(self, event_service):
        event = asyncio.get_event_loop().run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {"problem": "test"})
        )
        assert event.run_id == "run1"
        assert event.type == EventType.RUN_STARTED
        assert event.sequence == 1

    def test_emit_increments_sequence(self, event_service):
        loop = asyncio.get_event_loop()
        e1 = loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {})
        )
        e2 = loop.run_until_complete(
            event_service.emit("run1", EventType.AGENT_STARTED, {})
        )
        assert e2.sequence == 2

    def test_get_events_returns_all(self, event_service):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {})
        )
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_COMPLETED, {})
        )
        events = event_service.get_events("run1")
        assert len(events) == 2

    def test_subscribe_receives_events(self, event_service):
        queue = event_service.subscribe("run1")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {"problem": "x"})
        )
        assert not queue.empty()
        event = queue.get_nowait()
        assert event.type == EventType.RUN_STARTED

    def test_unsubscribe(self, event_service):
        queue = event_service.subscribe("run1")
        event_service.unsubscribe("run1", queue)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {})
        )
        assert queue.empty()

    def test_clear_run(self, event_service):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {})
        )
        event_service.clear_run("run1")
        assert event_service.get_events("run1") == []

    def test_get_event_count(self, event_service):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_STARTED, {})
        )
        loop.run_until_complete(
            event_service.emit("run1", EventType.RUN_COMPLETED, {})
        )
        assert event_service.get_event_count("run1") == 2

    def test_emit_with_string_event_type(self, event_service):
        event = asyncio.get_event_loop().run_until_complete(
            event_service.emit("run1", "custom_event", {"key": "value"})
        )
        assert event.type == "custom_event"
