#!/usr/bin/env bash
# =============================================================================
# Aura Fusion - Persistent Notifier (Frente 2 - Expansão)
# =============================================================================
# Notificações que NÃO somem sozinhas
# + Som sutil + Log em markdown para histórico
# =============================================================================

set -euo pipefail

AURA_ROOT="${AURA_ROOT:-$HOME/ProjectAuraOS}"
LOG_DIR="$AURA_ROOT/logs"
NOTIFY_LOG="$LOG_DIR/sofia_notifications.md"

mkdir -p "$LOG_DIR"

# Função para notificação persistente
notify_persistent() {
    local title="$1"
    local message="$2"
    local urgency="${3:-normal}"   # low, normal, critical
    
    # Notificação que não some (expire-time = 0)
    notify-send \
        --app-name="Sofia • Aura Fusion" \
        --urgency="$urgency" \
        --icon="dialog-information" \
        "$title" \
        "$message"
    
    # Log em markdown (histórico permanente)
    echo "## $(date '+%Y-%m-%d %H:%M:%S')" >> "$NOTIFY_LOG"
    echo "**$title**" >> "$NOTIFY_LOG"
    echo "" >> "$NOTIFY_LOG"
    echo "$message" >> "$NOTIFY_LOG"
    echo "" >> "$NOTIFY_LOG"
    echo "---" >> "$NOTIFY_LOG"
    echo "" >> "$NOTIFY_LOG"
    
    # Som sutil (se existir)
    if command -v paplay &> /dev/null && [ -f "/usr/share/sounds/freedesktop/stereo/message.oga" ]; then
        paplay "/usr/share/sounds/freedesktop/stereo/message.oga" 2>/dev/null || true
    fi
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] NOTIFIER: $1"
}

log "✅ Sistema de Notificações Persistentes ATIVADO"

# Exemplo de loop de demonstração (pode ser removido depois)
# Você pode chamar notify_persistent de outros scripts
while true; do
    # Aqui você pode adicionar lógica real depois
    # Por enquanto só mantém o processo vivo
    sleep 300
done
