"""
Control tools for Sofia.

These allow her to take actions on the system.
All dangerous operations require confirmation by default.
"""

import subprocess
import psutil
from ..base import BaseTool, ToolResult


class KillProcessTool(BaseTool):
    name = "kill_process"
    description = "Terminate a running process by PID. Requires confirmation."
    requires_confirmation = True

    def execute(self, pid: int, **kwargs) -> ToolResult:
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.terminate()
            return ToolResult(
                success=True,
                output=f"Process {pid} ({name}) terminated.",
                metadata={"pid": pid, "name": name}
            )
        except psutil.NoSuchProcess:
            return ToolResult(success=False, output=f"No process with PID {pid}")
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class RestartServiceTool(BaseTool):
    name = "restart_service"
    description = "Restart a systemd user service. Requires confirmation."
    requires_confirmation = True

    def execute(self, service_name: str, **kwargs) -> ToolResult:
        try:
            result = subprocess.run(
                ["systemctl", "--user", "restart", service_name],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return ToolResult(success=True, output=f"Service {service_name} restarted successfully.")
            else:
                return ToolResult(success=False, output=result.stderr or result.stdout)
        except Exception as e:
            return ToolResult(success=False, output=str(e))
