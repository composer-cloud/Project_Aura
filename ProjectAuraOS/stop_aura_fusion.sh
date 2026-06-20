#!/usr/bin/env bash
# =============================================================================
# Aura Fusion - Stop Script (Robusto)
# =============================================================================

set -euo pipefail

AURA_ROOT="${AURA_ROOT:-$HOME/ProjectAuraOS}"
PID_DIR="$AURA_ROOT/pids"
LOG_DIR="$AURA_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/aura_fusion.log"
}

log "🛑 Parando Aura Fusion..."

# Parar todos os processos conhecidos
for pidfile in "$PID_DIR"/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Parando processo PID $pid ($(basename $pidfile))"
            kill "$pid" 2>/dev/null || true
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pidfile"
    fi
done

# Matar por nome como fallback
pkill -f "autonomy_loop.py" 2>/dev/null || true
pkill -f "agente_v3.py" 2>/dev/null || true
pkill -f "aura_dashboard.py" 2>/dev/null || true
pkill -f "persistent_notifier.sh" 2>/dev/null || true

log "✅ Aura Fusion parado com sucesso."
