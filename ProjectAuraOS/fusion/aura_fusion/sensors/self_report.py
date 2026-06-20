"""
SelfReportSensor — the only truly safe sensor at the beginning.

Everything that enters here was voluntarily given by the user through
`sofia whisper`, shell integration, or explicit files.

This is how real presence begins without any surveillance risk.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from ..models import Event, EventKind
from .base import BaseSensor


class SelfReportSensor(BaseSensor):
    """
    Receives events injected from outside (CLI, scripts, future shell hooks).

    The sensor itself is passive: it just holds a queue that the daemon drains.
    """

    name = "self_report"

    def __init__(self, config):
        super().__init__(config)
        self._queue: deque[Event] = deque(maxlen=100)

    async def _on_start(self) -> None:
        # Nothing to do — we are purely reactive
        pass

    async def inject_whisper(self, text: str, context: dict | None = None) -> Event:
        """
        Called by the CLI or any trusted injection point.

        This is the primary way the user tells Sofia what is happening
        in their inner world.
        """
        event = Event(
            sensor=self.name,
            kind=EventKind.USER_WHISPER,
            subject=text[:512],  # keep subject reasonable
            metadata={
                "full_text": text,
                "injected_at": datetime.now(timezone.utc).isoformat(),
                **(context or {}),
            },
        )
        self._queue.append(event)
        return event

    async def sample(self) -> list[Event]:
        """Drain everything that was injected since last sample."""
        if not self.is_enabled:
            return []

        events = list(self._queue)
        self._queue.clear()
        return events
