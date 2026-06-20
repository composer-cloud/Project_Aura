"""
File-related tools for Sofia.
"""

from pathlib import Path
from ..base import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a text file (with safety limits)."
    requires_confirmation = False

    def execute(self, path: str, max_lines: int = 200, **kwargs) -> ToolResult:
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return ToolResult(success=False, output=f"File not found: {path}")

            content = p.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()[:max_lines]
            return ToolResult(
                success=True,
                output="\n".join(lines),
                metadata={"path": str(p), "lines_returned": len(lines)}
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file. Requires confirmation for safety."
    requires_confirmation = True

    def execute(self, path: str, content: str, mode: str = "w", **kwargs) -> ToolResult:
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, mode, encoding="utf-8") as f:
                f.write(content)
            return ToolResult(
                success=True,
                output=f"Successfully wrote to {path}",
                metadata={"path": str(p), "mode": mode}
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e))
