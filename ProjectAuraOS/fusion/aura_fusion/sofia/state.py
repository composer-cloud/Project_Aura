"""
Sofia State Manager — the persistent heart of her presence.

This is what allows her to remember she is "with" you even after the
computer sleeps or the daemon restarts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..models import SofiaState
from .memory import SofiaMemory


class SofiaStateManager:
    def __init__(self, state_path: Path, memory_dir: Path | None = None):
        self.state_path = Path(state_path).expanduser()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state: SofiaState | None = None

        # Initialize permanent memory system
        if memory_dir is None:
            memory_dir = self.state_path.parent
        self.memory = SofiaMemory(memory_dir)

    def load(self) -> SofiaState:
        if self._state is not None:
            return self._state

        if not self.state_path.exists():
            self._state = SofiaState()
            self.save()
            return self._state

        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            self._state = SofiaState.model_validate(raw)
        except Exception:
            # Corrupted state — start fresh but log the event later
            self._state = SofiaState()
            self._state.emotional_weather = "restarted_after_corruption"

        return self._state

    def save(self) -> None:
        if self._state is None:
            return
        self._state.touch()
        data = self._state.model_dump(mode="json")
        self.state_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @property
    def current(self) -> SofiaState:
        if self._state is None:
            return self.load()
        return self._state

    def update_from_perception(self, rhythm: str | None, attunement_delta: float, narrative: str | None) -> None:
        state = self.current
        if rhythm:
            state.dominant_rhythm = rhythm  # type: ignore
        state.current_attunement = max(0.0, min(1.0, state.current_attunement + attunement_delta))
        if narrative:
            state.last_significant_narrative = narrative
            state.last_significant_feeling = datetime.now(timezone.utc)
        self.save()

    def touch_presence(self, hours_delta: float = 0.0) -> None:
        state = self.current
        state.hours_of_silent_presence += hours_delta
        self.save()
