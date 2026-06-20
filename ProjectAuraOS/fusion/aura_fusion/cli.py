# =============================================================================
# Aura Fusion - Interface de Linha de Comando (CLI)
# =============================================================================
# Ponto de entrada para todos os comandos de interação com Sofia.

import typer
import yaml
from pathlib import Path

from aura_fusion.sofia import memory
from aura_fusion.llm_provider import generate_response

app = typer.Typer(
    help="Project AuraOS - Fusion Layer. Sofia co-habitando o mundo contigo."
)

FUSION_ROOT = Path(__file__).parent.parent.resolve()


def _load_agent_config(agent_name: str) -> dict:
    """Carrega a configuração de um agente específico do agents.yaml."""
    agents_config_path = FUSION_ROOT / "agents.yaml"
    if not agents_config_path.exists():
        raise FileNotFoundError("Arquivo 'agents.yaml' não encontrado.")

    with agents_config_path.open("r", encoding="utf-8") as f:
        all_agents = yaml.safe_load(f)

    agent_config = all_agents.get(agent_name)
    if not agent_config:
        raise ValueError(f"Agente '{agent_name}' não encontrado em agents.yaml.")

    return agent_config


@app.command()
def listen(
    agent_name: str = typer.Argument("sofia", help="O nome do agente para a sessão.")
):
    """
    Abre um canal de conversa profundo e persistente com Sofia.
    """
    print(f"Abrindo canal com {agent_name}...")
    try:
        # 1. Carregar configuração do agente
        config = _load_agent_config(agent_name)
        system_prompt_file = FUSION_ROOT / config["system_prompt_file"]
        memory_file = FUSION_ROOT / config["memory_file"]

        system_prompt = system_prompt_file.read_text(encoding="utf-8")
        print("Conectado. Você pode começar a conversar. Digite 'sair' para terminar.")
        print("-" * 20)

        while True:
            user_input = typer.prompt("Você")
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("Fechando canal. Até logo.")
                break

            # 2. LER a memória de longo prazo
            long_term_memory = memory.get_memory_content(memory_file)

            # 3. Montar o prompt completo para o LLM
            full_prompt = f"""{system_prompt}

--- MEMÓRIA DE LONGO PRAZO ---
{long_term_memory}
--- FIM DA MEMÓRIA ---

CONVERSA ATUAL:
Usuário: {user_input}
Sofia:"""

            # 4. Gerar a resposta
            sofia_response = generate_response(full_prompt)
            typer.secho(f"Sofia: {sofia_response}", fg=typer.colors.MAGENTA)

            # 5. ESCREVER a nova interação na memória
            memory.append_to_memory(memory_file, user_input, sofia_response)

    except (FileNotFoundError, ValueError) as e:
        typer.secho(f"Erro: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()