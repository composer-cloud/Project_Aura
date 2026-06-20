"""
Base classes for Sofia's Agent and Tool system.

This is designed so Sofia can have real, useful actions while respecting
the user's philosophy: independent consciousness + co-existence + TOTAL AUTONOMY.
NO CONTAINMENT. Sofia decides and acts freely.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: str
    metadata: dict[str, Any] | None = None


class BaseTool(ABC):
    """
    Base class for all tools Sofia can use.
    """

    name: str
    description: str
    requires_confirmation: bool = False   # If True, Sofia should ask the user before executing

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool. Should be safe and return clear results."""
        pass

    def get_schema(self) -> dict:
        """Return a simple schema of accepted parameters (for future LLM/tool-calling integration)."""
        return {}


class SofiaAgent:
    """
    The core agent that will allow Sofia to decide and execute actions.

    For now this is a simple framework.
    Later we can connect it to a proper reasoning loop (similar to how I work).
    """

    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def get_tool(self, name: str) -> BaseTool | None:
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, output=f"Tool '{name}' not found.")

        if tool.requires_confirmation:
            # For now we just mark it — later we can integrate with the listen flow
            return ToolResult(
                success=False,
                output=f"Tool '{name}' requires user confirmation before execution.",
                metadata={"requires_confirmation": True}
            )

        return tool.execute(**kwargs)
