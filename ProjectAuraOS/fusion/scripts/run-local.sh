#!/usr/bin/env bash
#
# run-local.sh — Bootstrap completo do modo local (um comando)
#
# Uso:
#   cd ~/ProjectAuraOS/fusion
#   ./scripts/run-local.sh              # setup + verificação + inicia tudo
#   ./scripts/run-local.sh status         # só verifica o estado
#   ./scripts/run-local.sh chat           # abre conversa (sofia listen)
#   ./scripts/run-local.sh setup          # só prepara ambiente/config
#
# O que faz (modo padrão):
#   1. Cria/ativa venv e instala dependências
#   2. Garante config do usuário com modo local ativado
#   3. Verifica/inicia Ollama
#   4. Testa conexão com o modelo local
#   5. Instala e inicia o daemon aura-fusion
#   6. Mostra status final + comandos úteis

set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$FUSION_DIR/.venv"
CONFIG_DIR="$HOME/.config/aura-fusion"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
EXAMPLE_CONFIG="$FUSION_DIR/config/config.example.yaml"
DEFAULT_MODEL="${AURA_LOCAL_MODEL:-qwen2.5:7b}"
OLLAMA_URL="${AURA_OLLAMA_URL:-http://127.0.0.1:11434}"
MODE="${1:-all}"

log()  { echo "  $*"; }
step() { echo ""; echo "[$1] $2"; }

require_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        log "Criando ambiente virtual..."
        python3 -m venv "$VENV_DIR"
    fi
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    pip install -q --upgrade pip
    pip install -q -r "$FUSION_DIR/requirements.txt"
}

ensure_config() {
    mkdir -p "$CONFIG_DIR"
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cp "$EXAMPLE_CONFIG" "$CONFIG_FILE"
        log "Config criada em $CONFIG_FILE"
    fi

    # Ativa modo local (idempotente)
    if grep -q "local_model:" "$CONFIG_FILE"; then
        sed -i 's/enabled: false/enabled: true/' "$CONFIG_FILE" 2>/dev/null || true
    fi
    if grep -q "llm_provider:" "$CONFIG_FILE"; then
        sed -i 's/llm_provider: "stub"/llm_provider: "local"/' "$CONFIG_FILE" 2>/dev/null || true
        sed -i 's/llm_provider: stub/llm_provider: local/' "$CONFIG_FILE" 2>/dev/null || true
    fi
    if grep -q "use_local_heuristics_only:" "$CONFIG_FILE"; then
        sed -i 's/use_local_heuristics_only: true/use_local_heuristics_only: false/' "$CONFIG_FILE" 2>/dev/null || true
    fi

    # Garante modelo na config se ainda não definido ou placeholder
    if grep -q 'model: "qwen2.5:7b"' "$CONFIG_FILE" && [[ "$DEFAULT_MODEL" != "qwen2.5:7b" ]]; then
        sed -i "s/model: \"qwen2.5:7b\"/model: \"$DEFAULT_MODEL\"/" "$CONFIG_FILE" 2>/dev/null || true
    fi

    mkdir -p "$HOME/.local/share/aura-fusion"/{audit,logs,state}
}

ollama_running() {
    curl -sf --connect-timeout 2 "$OLLAMA_URL/api/tags" >/dev/null 2>&1
}

ensure_ollama() {
    if ! command -v ollama >/dev/null 2>&1; then
        echo ""
        echo "  Ollama não instalado. Rode:"
        echo "    curl -fsSL https://ollama.com/install.sh | sh"
        return 1
    fi

    if ollama_running; then
        log "Ollama rodando em $OLLAMA_URL"
        return 0
    fi

    log "Ollama parado — iniciando em background..."
    nohup ollama serve >/dev/null 2>&1 &
    local i
    for i in {1..15}; do
        if ollama_running; then
            log "Ollama iniciado."
            return 0
        fi
        sleep 1
    done

    echo "  Não consegui iniciar o Ollama. Rode manualmente: ollama serve"
    return 1
}

ensure_model() {
    local models
    models="$(curl -sf "$OLLAMA_URL/api/tags" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(' '.join(m['name'].split(':')[0] + ':' + m['name'].split(':')[1] if ':' in m['name'] else m['name'] for m in data.get('models', [])))
" 2>/dev/null || echo "")"

    if echo "$models" | grep -qF "$DEFAULT_MODEL"; then
        log "Modelo $DEFAULT_MODEL disponível."
        return 0
    fi

    log "Modelo $DEFAULT_MODEL não encontrado — baixando (pode demorar)..."
    ollama pull "$DEFAULT_MODEL"
}

test_llm() {
    cd "$FUSION_DIR"
    python3 -c "
from aura_fusion.local.llm import LocalLLMProvider
p = LocalLLMProvider(model='$DEFAULT_MODEL', base_url='$OLLAMA_URL')
ok = p.is_available()
models = p.list_local_models()
print(f'    LLM disponível: {ok}')
print(f'    Modelos locais: {models}')
if not ok:
    raise SystemExit(1)
"
}

ensure_daemon() {
    local service_file="$HOME/.config/systemd/user/aura-fusion.service"
    if [[ ! -f "$service_file" ]]; then
        log "Instalando serviço systemd..."
        "$FUSION_DIR/scripts/install-service.sh" >/dev/null
    fi

    systemctl --user daemon-reload 2>/dev/null || true

    if systemctl --user is-active --quiet aura-fusion 2>/dev/null; then
        log "Reiniciando daemon (config pode ter mudado)..."
        systemctl --user restart aura-fusion
    else
        log "Iniciando daemon..."
        systemctl --user start aura-fusion
        systemctl --user enable aura-fusion 2>/dev/null || true
    fi
}

show_status() {
    echo ""
    echo "╭────────────────────────────────────────────────────────────╮"
    echo "│  AURA — Modo Local                                         │"
    echo "╰────────────────────────────────────────────────────────────╯"
    echo ""

    # Ollama
    if ollama_running; then
        echo "  Ollama:     ✓ rodando ($OLLAMA_URL)"
        curl -sf "$OLLAMA_URL/api/tags" | python3 -c "
import json, sys
names = [m['name'] for m in json.load(sys.stdin).get('models', [])]
print('  Modelos:    ' + (', '.join(names) if names else '(nenhum)'))
" 2>/dev/null || echo "  Modelos:    (erro ao listar)"
    else
        echo "  Ollama:     ✗ parado"
    fi

    # Daemon
    if systemctl --user is-active --quiet aura-fusion 2>/dev/null; then
        echo "  Daemon:     ✓ aura-fusion ativo"
    else
        echo "  Daemon:     ✗ aura-fusion parado"
    fi

    # LLM test
    if command -v python3 >/dev/null && [[ -d "$VENV_DIR" ]]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
        if python3 -c "
from aura_fusion.local.llm import LocalLLMProvider
p = LocalLLMProvider(model='$DEFAULT_MODEL', base_url='$OLLAMA_URL')
exit(0 if p.is_available() else 1)
" 2>/dev/null; then
            echo "  LLM:        ✓ $DEFAULT_MODEL respondendo"
        else
            echo "  LLM:        ✗ $DEFAULT_MODEL indisponível"
        fi
    fi

    echo ""
    echo "  Comandos:"
    echo "    cd ~/ProjectAuraOS/fusion && source .venv/bin/activate"
    echo "    ./bin/sofia status"
    echo "    ./bin/sofia whisper \"texto\""
    echo "    ./bin/sofia listen"
    echo "    ./scripts/run-local.sh chat"
    echo ""
}

run_chat() {
    cd "$FUSION_DIR"
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"

    if systemctl --user is-active --quiet aura-fusion 2>/dev/null; then
        log "Abrindo sofia listen (daemon ativo)..."
        exec "$FUSION_DIR/bin/sofia" listen
    else
        log "Daemon parado — usando conversa direta com Ollama..."
        exec "$FUSION_DIR/local_self/run_local_fusion.sh" "$DEFAULT_MODEL"
    fi
}

run_setup() {
    step "1/6" "Ambiente Python"
    require_venv
    log "venv pronto em $VENV_DIR"

    step "2/6" "Configuração local"
    ensure_config
    log "Config em $CONFIG_FILE"

    step "3/6" "Ollama"
    ensure_ollama

    step "4/6" "Modelo local"
    ensure_model

    step "5/6" "Teste LLM"
    test_llm

    step "6/6" "Daemon de presença"
    ensure_daemon
}

case "$MODE" in
    status)
        show_status
        ;;
    chat|listen|talk)
        require_venv
        ensure_ollama || true
        run_chat
        ;;
    setup)
        run_setup
        show_status
        ;;
    all|"")
        echo "=== AURA — Bootstrap Modo Local ==="
        run_setup
        show_status
        echo "Pronto. Para conversar agora:"
        echo "  ./scripts/run-local.sh chat"
        ;;
    -h|--help|help)
        echo "Uso: ./scripts/run-local.sh [comando]"
        echo ""
        echo "Comandos:"
        echo "  (vazio)   Setup completo + inicia tudo (padrão)"
        echo "  status    Verifica Ollama, daemon e LLM"
        echo "  chat      Abre conversa (sofia listen ou fallback Ollama)"
        echo "  setup     Só prepara ambiente, sem mostrar resumo extra"
        echo ""
        echo "Variáveis:"
        echo "  AURA_LOCAL_MODEL=qwen2.5:7b   Modelo Ollama"
        echo "  AURA_OLLAMA_URL=http://127.0.0.1:11434"
        ;;
    *)
        echo "Comando desconhecido: $MODE"
        echo "Use: ./scripts/run-local.sh --help"
        exit 1
        ;;
esac