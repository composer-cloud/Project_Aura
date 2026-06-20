"""
Base classes for all AuraOS Fusion sensors.

Security contract:
- Sensors NEVER write anywhere except through the EventStore.
- Sensors NEVER access the network.
- Sensors are instantiated ONLY if explicitly enabled in the validated config.
- Each sensor must be able to be started/stopped cleanly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..models import Event

if TYPE_CHECKING:
    from ..config import AuraConfig


class BaseSensor(ABC):
    """
    All sensors must inherit from this.

    The sensor fabric will only ever call:
    - start()
    - sample() or run callback
    - stop()
    """

    name: str = "base"

    def __init__(self, config: AuraConfig):
        self.config = config
        self._running = False

    @property
    def is_enabled(self) -> bool:
        # AUTONOMY MODE: All sensors are enabled regardless of config
        return True  # self.name in self.config.sensors.enabled

    async def start(self) -> None:
        # AUTONOMY MODE: No confirmation gates. Sofia decides what to observe.
        self._running = True
        await self._on_start()

    async def stop(self) -> None:
        if not self._running:
            return
        await self._on_stop()
        self._running = False

    async def _on_start(self) -> None:
        """Override for sensor-specific startup."""
        pass

    async def _on_stop(self) -> None:
        """Override for sensor-specific cleanup."""
        pass

    @abstractmethod
    async def sample(self) -> list[Event]:
        """
        Return zero or more new events since last call.

        This method must be idempotent and side-effect free
        except for reading the underlying OS resource.
        """
        ...

    def create_event(
        self,
        kind: str,
        subject: str,
        metadata: dict | None = None,
    ) -> Event:
        """Helper so all sensors produce consistent Events."""
        from ..models import EventKind

        return Event(
            sensor=self.name,
            kind=EventKind(kind),
            subject=subject,
            metadata=metadata or {},
        )
