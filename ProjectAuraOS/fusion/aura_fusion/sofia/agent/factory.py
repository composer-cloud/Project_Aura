"""
Factory for creating SofiaAgent instances with the right tools.
"""

from .base import SofiaAgent
from .tools.system import SystemStatusTool, RunCommandTool
from .tools.files import ReadFileTool, WriteFileTool
from .tools.memory import AddToMemoryTool
from .tools.introspection import GetRecentMemoriesTool, GetSemanticFactsTool
from .tools.monitoring import (
    CPUUsageTool,
    MemoryUsageTool,
    DiskUsageTool,
    ProcessListTool,
    NetworkConnectionsTool,
)
from .tools.control import KillProcessTool, RestartServiceTool
from ..memory import SofiaMemory


def create_default_agent(memory: SofiaMemory) -> SofiaAgent:
    """
    Creates a SofiaAgent with a balanced set of initial tools.
    """
    agent = SofiaAgent()

    # Register safe / low-risk tools
    agent.register_tool(SystemStatusTool())
    agent.register_tool(ReadFileTool())
    agent.register_tool(AddToMemoryTool(memory))
    agent.register_tool(GetRecentMemoriesTool(memory))
    agent.register_tool(GetSemanticFactsTool(memory))

    # Monitoring tools (read-only, safe)
    agent.register_tool(CPUUsageTool())
    agent.register_tool(MemoryUsageTool())
    agent.register_tool(DiskUsageTool())
    agent.register_tool(ProcessListTool())
    agent.register_tool(NetworkConnectionsTool())

    # Register tools that require confirmation by default (sensitive actions)
    agent.register_tool(RunCommandTool())
    agent.register_tool(WriteFileTool())
    agent.register_tool(KillProcessTool())
    agent.register_tool(RestartServiceTool())

    return agent
