# =============================================================================
# Aura Fusion - Módulo de Memória do Agente
# =============================================================================
# Responsável por ler e escrever na memória de longo prazo de um agente.

import datetime
from pathlib import Path


class SofiaMemory:
    """
    Gerencia a memória de longo prazo da Sofia, armazenada em um arquivo markdown.
    """
    def __init__(self, memory_dir: Path):
        """
        Inicializa o sistema de memória.

        Args:
            memory_dir: O diretório onde o arquivo de memória será armazenado.
        """
        self.memory_file = Path(memory_dir) / "sofia_memory.md"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def get_content(self) -> str:
        """
        Lê o conteúdo do arquivo de memória de longo prazo.

        Retorna uma string vazia se o arquivo não existir.
        """
        if not self.memory_file.exists():
            return ""
        try:
            return self.memory_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️  Erro ao ler o arquivo de memória {self.memory_file}: {e}")
            return ""

    def append(self, user_input: str, sofia_response: str):
        """
        Adiciona uma nova entrada de memória ao arquivo de longo prazo.

        A entrada é formatada com timestamp para contexto.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"""
---
**Timestamp:** {timestamp}

**Usuário:** {user_input}

**Sofia:** {sofia_response}
"""

        try:
            with self.memory_file.open("a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"⚠️  Erro ao escrever no arquivo de memória {self.memory_file}: {e}")
