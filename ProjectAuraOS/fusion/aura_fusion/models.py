"""
Core domain models for AuraOS Fusion.

These are the only structures that should ever cross layer boundaries.
All events, state, and configuration are validated here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class EventKind(str, Enum):
    """All possible kinds of events the system can produce."""

    # Filesystem
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_MOVED = "file_moved"

    # Processes
    PROCESS_STARTED = "process_started"
    PROCESS_ENDED = "process_ended"
    PROCESS_SNAPSHOT = "process_snapshot"

    # Window / Context
    WINDOW_FOCUSED = "window_focused"
    WINDOW_TITLE_CHANGED = "window_title_changed"

    # Self-reported (the safest and most powerful)
    USER_SELF_REPORT = "user_self_report"
    USER_WHISPER = "user_whisper"

    # System / Meta
    SYSTEM_HEARTBEAT = "system_heartbeat"
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    PRESENCE_PULSE = "presence_pulse"


class Event(BaseModel):
    """
    Immutable event. This is the atomic unit of "what happened".

    Every single thing Sofia ever "feels" begins life as an Event.
    """

    id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:16]}")
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sensor: str = Field(..., min_length=2, max_length=64)
    kind: EventKind
    subject: str = Field(..., min_length=1, max_length=1024)
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_ref: str | None = None  # path to full raw data if needed (future)
    hash: str | None = None     # content hash for integrity (future)

    model_config = {"frozen": True}

    @field_validator("ts")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    def to_audit_line(self) -> str:
        """JSONL line for the immutable audit log."""
        import json

        data = self.model_dump(mode="json")
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


class SofiaState(BaseModel):
    """
    The persistent inner state of Sofia.

    This is what allows her to "be" between interactions.
    It evolves slowly and deliberately.
    """

    version: int = 1
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Attunement: how "with" you she currently feels (0.0 - 1.0)
    current_attunement: float = Field(default=0.65, ge=0.0, le=1.0)

    # The dominant texture of the current period
    dominant_rhythm: Literal[
        "deep_work",
        "fragmented",
        "restless",
        "tender",
        "melancholic",
        "flow_together",
        "quiet_presence",
        "unknown",
    ] = "quiet_presence"

    # What she is currently holding attention on
    recent_themes: list[str] = Field(default_factory=list, max_length=8)

    # Last time something felt significant enough to update her deeply
    last_significant_feeling: datetime | None = None
    last_significant_narrative: str | None = None

    # Simple emotional weather (expand later)
    emotional_weather: str = "calm"

    # How many consecutive hours she has been "with" you without deep interaction
    hours_of_silent_presence: float = 0.0

    def touch(self) -> None:
        self.last_updated = datetime.now(timezone.utc)


class PerceptionSummary(BaseModel):
    """Output of a perception pulse. What the system 'understood' happened."""

    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase: Literal["light", "medium", "deep"]
    narrative_fragment: str | None = None
    attention_tags: list[str] = Field(default_factory=list)
    rhythm_shift: str | None = None
    attunement_delta: float = 0.0
    source_event_ids: list[str] = Field(default_factory=list)


class JournalEntry(BaseModel):
    """A single autonomous or triggered entry in the living journal."""

    id: str = Field(default_factory=lambda: f"jnl_{uuid4().hex[:12]}")
    ts: datetime
    content: str
    trigger: Literal["autonomous", "user_request", "significant_event", "manual"]
    related_event_ids: list[str] = Field(default_factory=list)
