"""
Basic system tools for Sofia.
"""

import subprocess
from ..base import BaseTool, ToolResult


class SystemStatusTool(BaseTool):
    name = "system_status"
    description = "Get basic information about the current system (uptime, load, memory, etc)."
    requires_confirmation = False

    def execute(self, **kwargs) -> ToolResult:
        try:
            result = subprocess.run(
                ["uptime", "&&", "free", "-h", "&&", "df", "-h", "/"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return ToolResult(
                success=True,
                output=result.stdout or result.stderr,
                metadata={"command": "system_status"}
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class RunCommandTool(BaseTool):
    """
    Allows Sofia to run shell commands.
    Dangerous commands should require confirmation.
    """

    name = "run_command"
    description = "Execute a shell command on the system."
    requires_confirmation = True   # Default to requiring confirmation for safety

    def execute(self, command: str, **kwargs) -> ToolResult:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout or result.stderr,
                metadata={"command": command, "returncode": result.returncode}
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e))
