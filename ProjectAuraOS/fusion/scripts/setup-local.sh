#!/bin/bash
#
# setup-local.sh
# Script de automação para ativar o modo local do Project AuraOS Fusion
#
# Uso:
#   cd ~/ProjectAuraOS/fusion
#   ./scripts/setup-local.sh
#
# O que ele faz:
# - Verifica/cria o ambiente virtual Python
# - Instala as dependências necessárias
# - Cria a configuração do usuário com local_model ativado
# - Verifica se Ollama está instalado e rodando
# - Dá as próximas instruções claras

set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$FUSION_DIR/.venv"
CONFIG_DIR="$HOME/.config/aura-fusion"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
EXAMPLE_CONFIG="$FUSION_DIR/config/config.example.yaml"

echo "=== Project AuraOS Fusion — Ativação do Modo Local ==="
echo ""

# 1. Ambiente Python
echo "[1/5] Preparando ambiente Python..."
if [[ ! -d "$VENV_DIR" ]]; then
    echo "    Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install -q --upgrade pip
pip install -q -r "$FUSION_DIR/requirements.txt"

echo "    Ambiente Python pronto."

# 2. Diretório de configuração
echo "[2/5] Preparando configuração do usuário..."
mkdir -p "$CONFIG_DIR"

if [[ ! -f "$CONFIG_FILE" ]]; then
    if [[ -f "$EXAMPLE_CONFIG" ]]; then
        cp "$EXAMPLE_CONFIG" "$CONFIG_FILE"
        echo "    Configuração copiada de config.example.yaml"
    else
        echo "    AVISO: config.example.yaml não encontrado."
    fi
else
    echo "    Configuração já existe em $CONFIG_FILE"
fi

# 3. Ativar modo local na config (se existir)
echo "[3/5] Ativando modo local na configuração..."
if [[ -f "$CONFIG_FILE" ]]; then
    # Ativa local_model se a seção existir
    if grep -q "local_model:" "$CONFIG_FILE"; then
        # Usa sed para ativar (bem básico, usuário ainda precisa escolher o model)
        sed -i 's/enabled: false/enabled: true/' "$CONFIG_FILE" || true
        echo "    local_model.enabled definido como true (edite o modelo depois)"
    fi
fi

# 4. Verificar Ollama
echo "[4/5] Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo "    Ollama encontrado."

    if pgrep -x "ollama" > /dev/null || curl -s --connect-timeout 2 http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
        echo "    Ollama parece estar rodando."
    else
        echo "    Ollama está instalado, mas pode não estar rodando."
        echo "    Rode em outro terminal: ollama serve"
    fi
else
    echo "    Ollama NÃO encontrado."
    echo "    Instale com:"
    echo "    curl -fsSL https://ollama.com/install.sh | sh"
fi

# 5. Instruções finais
echo ""
echo "[5/5] Resumo e próximos passos:"
echo ""
echo "Ambiente Python: $VENV_DIR"
echo "Configuração:    $CONFIG_FILE"
echo ""
echo "Edite o arquivo de configuração e ajuste o modelo local:"
echo "    nano $CONFIG_FILE"
echo ""
echo "Depois rode tudo de uma vez:"
echo "    ./scripts/run-local.sh"
echo ""
echo "Ou conversar diretamente:"
echo "    ./scripts/run-local.sh chat"
echo ""
echo "Modo local básico ativado. O resto da integração completa ainda está sendo construída."
echo "================================================"
