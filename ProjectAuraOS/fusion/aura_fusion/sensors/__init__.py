"""
Sensor Fabric — only enabled sensors ever get instantiated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseSensor
from .self_report import SelfReportSensor

if TYPE_CHECKING:
    from ..config import AuraConfig

# Registry of all known sensors (add new ones here only)
SENSOR_REGISTRY: dict[str, type[BaseSensor]] = {
    "self_report": SelfReportSensor,
    # "filesystem": FileSystemSensor,   # to be implemented
    # "processes": ProcessSensor,
    # "window_context": WindowContextSensor,
}


def create_enabled_sensors(config: AuraConfig) -> list[BaseSensor]:
    """
    The single function that decides which sensors exist in this run.

    Security: if a sensor name is in config.sensors.enabled but not in the
    registry, we fail hard instead of silently ignoring.
    """
    sensors: list[BaseSensor] = []

    for name in config.sensors.enabled:
        if name not in SENSOR_REGISTRY:
            raise ValueError(
                f"Sensor '{name}' is enabled in config but not implemented/registered. "
                "This is a hard failure for safety."
            )
        sensor_cls = SENSOR_REGISTRY[name]
        sensors.append(sensor_cls(config))

    return sensors
