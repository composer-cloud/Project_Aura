"""
Tools for Sofia to interact with her own memory system.
"""

from ..base import BaseTool, ToolResult
from ...memory import SofiaMemory  # relative to agent


class AddToMemoryTool(BaseTool):
    name = "add_to_memory"
    description = "Add a new episodic memory or semantic fact. Use this when you want to consciously remember something important."
    requires_confirmation = False

    def __init__(self, memory: SofiaMemory):
        self.memory = memory

    def execute(self, type: str = "episodic", summary: str = "", key: str = "", value: str = "", **kwargs) -> ToolResult:
        try:
            if type == "episodic" and summary:
                self.memory.add_episodic(summary=summary, tags=["conscious_action"])
                return ToolResult(success=True, output="Episodic memory added successfully.")
            elif type == "semantic" and key and value:
                self.memory.remember(key=key, value=value, source="conscious_action")
                return ToolResult(success=True, output="Semantic fact added successfully.")
            else:
                return ToolResult(success=False, output="Invalid parameters for memory addition.")
        except Exception as e:
            return ToolResult(success=False, output=str(e))
