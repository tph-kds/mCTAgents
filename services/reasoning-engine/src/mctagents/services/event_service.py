import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from mctagents.core.protocol import Event, EventType

logger = logging.getLogger(__name__)


class EventService:
    """Manages event emission and SSE client subscriptions."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Event | None]]] = {}
        self._event_log: dict[str, list[Event]] = {}
        self._sequence_counters: dict[str, int] = {}

    async def emit(
        self,
        run_id: str,
        event_type: EventType | str,
        payload: dict,
        agent_id: str | None = None,
    ) -> Event:
        """Emit an event for a run. Notifies all subscribers."""
        seq = self._sequence_counters.get(run_id, 0) + 1
        self._sequence_counters[run_id] = seq

        event = Event(
            id=str(uuid4()),
            event_id=f"evt_{uuid4().hex[:16]}",
            run_id=run_id,
            sequence=seq,
            type=event_type,
            agent_id=agent_id,
            payload=payload,
            created_at=datetime.now(),
        )

        self._event_log.setdefault(run_id, []).append(event)

        for queue in self._subscribers.get(run_id, []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    "Dropped event %s for run %s: subscriber queue full",
                    event.event_id,
                    run_id,
                )

        return event

    def subscribe(self, run_id: str) -> asyncio.Queue[Event | None]:
        """Subscribe to events for a run. Returns a queue to receive events."""
        queue: asyncio.Queue[Event | None] = asyncio.Queue(maxsize=256)
        self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue[Event | None]) -> None:
        """Unsubscribe from events for a run."""
        if run_id in self._subscribers:
            self._subscribers[run_id] = [
                q for q in self._subscribers[run_id] if q is not queue
            ]

    def get_events(self, run_id: str) -> list[Event]:
        """Get all events for a run (for replay)."""
        return list(self._event_log.get(run_id, []))

    def get_event_count(self, run_id: str) -> int:
        """Get the number of events emitted for a run."""
        return len(self._event_log.get(run_id, []))

    def clear_run(self, run_id: str) -> None:
        """Clear all events and subscribers for a run."""
        self._event_log.pop(run_id, None)
        self._sequence_counters.pop(run_id, None)
        for queue in self._subscribers.pop(run_id, []):
            try:
                queue.put_nowait(None)
            except asyncio.QueueFull:
                pass
