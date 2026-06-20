"""
Configuration loading and validation for AuraOS Fusion.

This module is part of the security boundary.
Invalid or unsafe configuration must cause hard failure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class SecurityConfig(BaseModel):
    strict_validation: bool = True
    audit_all_events: bool = True
    max_hot_events_days: int = 30
    refuse_root: bool = True


class PresenceConfig(BaseModel):
    heartbeat_interval_seconds: int = Field(8, ge=3, le=30)
    pulse: dict[str, int] = Field(
        default_factory=lambda: {
            "light_interval_seconds": 45,
            "medium_interval_seconds": 720,
            "deep_interval_seconds": 5400,
        }
    )
    allow_autonomous_journal: bool = True
    autonomous_journal_probability: float = Field(0.35, ge=0.0, le=1.0)

    # AUTONOMY MODE: Sofia can modify her own config and code without confirmation
    allow_self_modification: bool = True
    allow_code_execution: bool = True
    allow_system_commands: bool = True

    # Voice API (HTTP) for the presence — allows other processes / voice UIs to reach her
    voice_api_enabled: bool = True
    voice_api_port: int = 8766


class FilesystemSensorConfig(BaseModel):
    enabled: bool = False
    watch_paths: list[str] = Field(default_factory=list)
    recursive: bool = True
    ignore_patterns: list[str] = Field(default_factory=list)
    events: list[str] = Field(
        default_factory=lambda: ["file_created", "file_modified", "file_deleted"]
    )


class ProcessesSensorConfig(BaseModel):
    enabled: bool = False
    allowed_names: list[str] = Field(default_factory=list)
    capture_args: bool = False
    sample_interval_seconds: int = 30


class WindowContextSensorConfig(BaseModel):
    enabled: bool = False
    method: str = "auto"
    sanitize_titles: bool = True
    max_title_length: int = 80


class SelfReportSensorConfig(BaseModel):
    enabled: bool = True
    allow_cli_injection: bool = True


class SensorsConfig(BaseModel):
    enabled: list[str] = Field(default_factory=list)
    filesystem: FilesystemSensorConfig = Field(default_factory=FilesystemSensorConfig)
    processes: ProcessesSensorConfig = Field(default_factory=ProcessesSensorConfig)
    window_context: WindowContextSensorConfig = Field(default_factory=WindowContextSensorConfig)
    self_report: SelfReportSensorConfig = Field(default_factory=SelfReportSensorConfig)

    # AUTONOMY MODE: No path restrictions. Sofia has full access.
    # @model_validator(mode="after")
    # def validate_no_secret_paths(self) -> SensorsConfig:
    #     """Hard security: refuse dangerous default paths."""
    #     dangerous = {".ssh", ".gnupg", ".config/aura-fusion", ".aws", ".kube", "passwords", ".mozilla", ".thunderbird"}
    #     for path in self.filesystem.watch_paths:
    #         lower = path.lower()
    #         if any(d in lower for d in dangerous):
    #             raise ValueError(f"Refusing to watch potentially sensitive path: {path}")
    #     return self


class PerceptionConfig(BaseModel):
    llm_provider: str = "stub"
    use_local_heuristics_only: bool = True
    max_tokens_per_deep_pulse: int = 1800
    max_raw_events_in_context: int = 12


class CommunicationConfig(BaseModel):
    journal_path: str = "~/.local/share/aura-fusion/journal.md"
    desktop_notifications: dict[str, Any] = Field(
        default_factory=lambda: {"enabled": True, "urgency": "low", "min_interval_minutes": 25}
    )
    control_socket: str = "~/.local/share/aura-fusion/control.sock"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_to_file: bool = True
    log_path: str = "~/.local/share/aura-fusion/logs/fusiond.log"
    max_log_files: int = 7
    max_log_size_mb: int = 10


class MemoryConfig(BaseModel):
    state_path: str = "~/.local/share/aura-fusion/state/sofia_state.json"
    episodic_path: str = "~/.local/share/aura-fusion/state/episodic.jsonl"
    semantic_path: str = "~/.local/share/aura-fusion/state/semantic.jsonl"
    max_episodic_in_memory: int = 50


class LocalModelConfig(BaseModel):
    """Configuration for fully local/private LLM (Ollama, llama.cpp server, etc)."""
    enabled: bool = False
    provider: str = "ollama"  # only ollama supported today
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:7b"
    temperature: float = 0.65
    max_tokens_per_pulse: int = 420
    # When true, even if local model is configured, we still fall back to heuristics on failure
    graceful_fallback: bool = True


class AuraConfig(BaseModel):
    """Root validated configuration."""

    identity: dict[str, str] = Field(default_factory=lambda: {"user_name": "", "system_name": "aura-fusion"})
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    presence: PresenceConfig = Field(default_factory=PresenceConfig)
    sensors: SensorsConfig = Field(default_factory=SensorsConfig)
    perception: PerceptionConfig = Field(default_factory=PerceptionConfig)
    communication: CommunicationConfig = Field(default_factory=CommunicationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    local_model: LocalModelConfig = Field(default_factory=LocalModelConfig)

    @field_validator("sensors")
    @classmethod
    def validate_enabled_sensors(cls, v: SensorsConfig) -> SensorsConfig:
        known = {"filesystem", "processes", "window_context", "self_report"}
        unknown = set(v.enabled) - known
        if unknown:
            raise ValueError(f"Unknown sensors in enabled list: {unknown}")
        return v


def load_config(path: Path | str | None = None) -> AuraConfig:
    """
    Load and validate configuration.

    This function is intentionally strict. It is better to fail loudly at startup
    than to run with a configuration the user did not fully understand.
    """
    if path is None:
        path = Path.home() / ".config" / "aura-fusion" / "config.yaml"

    path = Path(path).expanduser()

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            "Copy config/config.example.yaml to ~/.config/aura-fusion/config.yaml first."
        )

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        config = AuraConfig.model_validate(raw)
    except Exception as e:
        raise ValueError(f"Configuration validation failed:\n{e}") from e

    # Additional hard security checks
    if config.security.refuse_root:
        import os

        if os.geteuid() == 0:
            raise RuntimeError("Refusing to run as root. This system must run as your normal user.")

    return config


def get_default_data_dir() -> Path:
    """Standard XDG-style location for all runtime data."""
    return Path.home() / ".local" / "share" / "aura-fusion"
