#!/usr/bin/env bash
#
# Project AuraOS Fusion — Service Installation
# This script sets up the systemd --user service safely.

set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_FILE="$FUSION_DIR/scripts/aura-fusion.service"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
TARGET_SERVICE="$SYSTEMD_USER_DIR/aura-fusion.service"

echo "==> Project AuraOS Fusion — Instalando serviço de presença"

# 1. Check for venv
if [ ! -d "$FUSION_DIR/.venv" ]; then
    echo "!! Ambiente virtual não encontrado."
    echo "   Cria com:"
    echo "     python3 -m venv \"$FUSION_DIR/.venv\""
    echo "     source \"$FUSION_DIR/.venv/bin/activate\""
    echo "     pip install -r \"$FUSION_DIR/requirements.txt\""
    exit 1
fi

# 2. Ensure config exists
CONFIG_DIR="$HOME/.config/aura-fusion"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    echo "==> Copiando configuração de exemplo (tudo desativado por padrão)"
    cp "$FUSION_DIR/config/config.example.yaml" "$CONFIG_DIR/config.yaml"
    echo "    Edita $CONFIG_DIR/config.yaml antes de ativar sensores."
fi

# 3. Create data directories
mkdir -p "$HOME/.local/share/aura-fusion"/{audit,logs,state}

# 4. Install systemd unit
mkdir -p "$SYSTEMD_USER_DIR"
cp "$SERVICE_FILE" "$TARGET_SERVICE"

echo "==> Recarregando systemd --user"
systemctl --user daemon-reload

echo ""
echo "==> Serviço instalado com sucesso."
echo ""
echo "Comandos úteis:"
echo "  systemctl --user start aura-fusion     # Iniciar agora"
echo "  systemctl --user enable aura-fusion    # Iniciar no login"
echo "  systemctl --user status aura-fusion"
echo "  journalctl --user -u aura-fusion -f"
echo ""
echo "Depois de iniciar, experimenta:"
echo "  ~/ProjectAuraOS/fusion/bin/sofia status"
echo ""
echo "Lembra-te: por padrão NENHUM sensor está ativo."
echo "Presença silenciosa já é suficiente no começo."
