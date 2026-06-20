"""
Autonomy Loop

This is the main continuous loop that will give Sofia real independent operation.

It runs alongside (or inside) the daemon and gives her the ability to:
- Observe the computer usage over time
- Build her own understanding of the user's patterns
- Take actions with high autonomy when it makes sense
- Record her own reflections and learning

This is the foundation for "maximum autonomy".
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AutonomyEngine


class AutonomyLoop:
    """
    Long-running autonomy loop.
    This is what will allow Sofia to "live" on the user's machine with real independence.
    """

    def __init__(self, engine: AutonomyEngine):
        self.engine = engine
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the continuous autonomy loop."""
        if self._task and not self._task.done():
            return

        print("[AutonomyLoop] Starting high-autonomy loop...")
        self._task = asyncio.create_task(self.engine.start())

    async def stop(self):
        """Stop the autonomy loop gracefully."""
        if self._task:
            self.engine.stop()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            print("[AutonomyLoop] Stopped.")

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()
