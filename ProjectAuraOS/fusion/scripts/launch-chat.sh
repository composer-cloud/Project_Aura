#!/usr/bin/env bash
# =============================================================================
# Aura Fusion - Lançador do Chat com Sofia
# =============================================================================
# Este script é chamado pelo atalho da área de trabalho para iniciar
# uma sessão de chat interativa em uma nova janela de terminal.

set -e

# Garante que estamos no diretório correto do projeto
cd "$(dirname "$0")/.."

# Ativa o ambiente virtual Python
source .venv/bin/activate

# Abre um novo terminal e executa o comando 'listen'.
# 'x-terminal-emulator' é um comando genérico que deve abrir o seu terminal padrão.
x-terminal-emulator -e "python -m aura_fusion.cli listen"