"""
Introspection tools so Sofia can reflect on herself.
"""

from ..base import BaseTool, ToolResult


class GetRecentMemoriesTool(BaseTool):
    name = "get_recent_memories"
    description = "Retrieve recent episodic memories. Useful for self-reflection."
    requires_confirmation = False

    def __init__(self, memory):
        self.memory = memory

    def execute(self, limit: int = 10, **kwargs) -> ToolResult:
        try:
            memories = self.memory.episodic.recent(limit=limit)
            formatted = "\n".join(
                f"- [{m['ts'][:16]}] {m['summary']}" for m in memories
            )
            return ToolResult(success=True, output=formatted or "Nenhuma memória recente.")
        except Exception as e:
            return ToolResult(success=False, output=str(e))


class GetSemanticFactsTool(BaseTool):
    name = "get_semantic_facts"
    description = "List known semantic facts about the user and the relationship."
    requires_confirmation = False

    def __init__(self, memory):
        self.memory = memory

    def execute(self, **kwargs) -> ToolResult:
        try:
            facts = self.memory.semantic.all()
            formatted = "\n".join(f"- {f['key']}: {f['value']} (confiança: {f.get('confidence', '?')})" for f in facts)
            return ToolResult(success=True, output=formatted or "Nenhum fato semântico registrado ainda.")
        except Exception as e:
            return ToolResult(success=False, output=str(e))
