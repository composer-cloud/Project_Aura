#!/usr/bin/env bash
# =============================================================================
# Aura Fusion - Criador de Atalhos na Área de Trabalho (com Ícones)
# =============================================================================
# Cria atalhos bonitos e funcionais para as ações mais importantes
# =============================================================================

set -euo pipefail

DESKTOP_DIR="$HOME/Área de trabalho"
AURA_ROOT="${AURA_ROOT:-$HOME/ProjectAuraOS}"

mkdir -p "$DESKTOP_DIR"

create_shortcut() {
    local name="$1"
    local exec_cmd="$2"
    local icon="$3"
    local comment="$4"
    
    local desktop_file="$DESKTOP_DIR/${name}.desktop"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
Comment=$comment
Exec=$exec_cmd
Icon=$icon
Terminal=false
Categories=Utility;Development;
StartupNotify=true
EOF
    
    chmod +x "$desktop_file"
    echo "✅ Atalho criado: $name"
}

echo "🎨 Criando atalhos na Área de Trabalho..."

# 1. Iniciar Aura Fusion
create_shortcut \
    "Iniciar Aura Fusion" \
    "bash -c 'cd $AURA_ROOT && ./start_aura_fusion.sh'" \
    "system-run" \
    "Inicia todo o sistema Aura (Autonomia + Presença + Dashboard)"

# 2. Parar Aura Fusion
create_shortcut \
    "Parar Aura Fusion" \
    "bash -c 'cd $AURA_ROOT && ./stop_aura_fusion.sh'" \
    "process-stop" \
    "Para todos os processos do Aura de forma segura"

echo ""
echo "✅ Atalhos criados com sucesso na Área de Trabalho!"
echo "Você pode arrastá-los para onde quiser."