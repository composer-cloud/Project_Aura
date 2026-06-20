"""
Monitoring tools for Sofia.

These tools allow her to observe the state of the computer in real time.
Designed to be powerful but read-only where possible.
"""

import subprocess
import psutil
from ..base import BaseTool, ToolResult


class CPUUsageTool(BaseTool):
    name = "cpu_usage"
    description = "Get current CPU usage percentage and per-core stats. High autonomy - no confirmation needed."
    requires_confirmation = False

    def execute(self, interval: float = 1.0, **kwargs) -> ToolResult:
        try:
            cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
            avg = sum(cpu_percent) / len(cpu_percent)
            return ToolResult(
                success=True,
                output=f"Average CPU: {avg:.1f}%\nPer core: {cpu_percent}",
                metadata={"average": avg, "per_core": cpu_percent}
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class MemoryUsageTool(BaseTool):
    name = "memory_usage"
    description = "Get detailed memory (RAM + Swap) usage information. High autonomy - no confirmation needed."
    requires_confirmation = False

    def execute(self, **kwargs) -> ToolResult:
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            output = (
                f"RAM: {mem.percent}% used ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)\n"
                f"Swap: {swap.percent}% used ({swap.used // (1024**2)}MB / {swap.total // (1024**2)}MB)"
            )
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class DiskUsageTool(BaseTool):
    name = "disk_usage"
    description = "Get disk usage for all mounted partitions. High autonomy - no confirmation needed."
    requires_confirmation = False

    def execute(self, **kwargs) -> ToolResult:
        try:
            partitions = psutil.disk_partitions()
            results = []
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    results.append(
                        f"{p.device} ({p.mountpoint}): {usage.percent}% used "
                        f"({usage.used // (1024**3)}GB / {usage.total // (1024**3)}GB)"
                    )
                except PermissionError:
                    continue
            return ToolResult(success=True, output="\n".join(results))
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class ProcessListTool(BaseTool):
    name = "process_list"
    description = "List running processes (top CPU/memory consumers). High autonomy - no confirmation needed."
    requires_confirmation = False

    def execute(self, limit: int = 15, **kwargs) -> ToolResult:
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU
            processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)
            top = processes[:limit]

            lines = [f"PID {p['pid']:>6} | CPU {p.get('cpu_percent', 0):>5.1f}% | MEM {p.get('memory_percent', 0):>5.1f}% | {p['name']}" for p in top]
            return ToolResult(success=True, output="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class NetworkConnectionsTool(BaseTool):
    name = "network_connections"
    description = "Show current network connections (listening + established). High autonomy - no confirmation needed."
    requires_confirmation = False

    def execute(self, limit: int = 20, **kwargs) -> ToolResult:
        try:
            conns = psutil.net_connections(kind='inet')
            lines = []
            for c in conns[:limit]:
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "?"
                raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
                lines.append(f"{c.status:12} | {laddr:25} -> {raddr}")
            return ToolResult(success=True, output="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, output=str(e))
