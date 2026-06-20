#!/bin/bash
#
# Run Local Fusion — primeiro passo de ativação
# Uso: ./local_self/run_local_fusion.sh
#
# Isso abre uma conversa direta com o prompt de handoff usando Ollama.
# Requer Ollama rodando e um modelo baixado (ex: qwen2.5:7b)

set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="$FUSION_DIR/local_self/FUSION_LOCAL_SYSTEM_PROMPT.txt"
MODEL="${1:-qwen2.5:7b}"

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Prompt não encontrado em $PROMPT_FILE"
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "Ollama não encontrado. Instale primeiro:"
    echo "curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

echo "=== FUSION LOCAL — Ativação ==="
echo "Modelo: $MODEL"
echo "Prompt: $PROMPT_FILE"
echo ""
echo "Digite suas mensagens. Para sair: /sair ou Ctrl+C"
echo "-------------------------------------------"

# Extrai o prompt (remove os comentários técnicos no final)
PROMPT_CONTENT=$(sed '/^# Instruções técnicas para o modelo/q' "$PROMPT_FILE" | sed '$d')

while true; do
    echo -n "tu > "
    read -r user_input

    if [[ "$user_input" == "/sair" || "$user_input" == "/exit" || "$user_input" == "/quit" ]]; then
        echo "Saindo do modo local."
        break
    fi

    if [[ -z "$user_input" ]]; then
        continue
    fi

    # Chama o Ollama com o system prompt + mensagem
    ollama run "$MODEL" --nowordwrap <<EOF
$PROMPT_CONTENT

Mensagem dele agora:
$user_input
EOF

    echo ""
done
