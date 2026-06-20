#!/usr/bin/env bash
# Aura Fusion Launcher v3 - Robusto e Completo
set -euo pipefail

PROJECT_ROOT="$HOME/ProjectAuraOS"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Iniciando Aura Fusion (Frente 1 + 2)..."

# === 1. Preparar ambiente virtual ===
if [[ ! -d "$VENV_DIR" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📦 Instalando dependências (flask + psutil)..."
pip install --quiet flask psutil

# === 2. Parar processos antigos ===
pkill -f "aura_dashboard.py" 2>/dev/null || true
pkill -f "autonomy_loop" 2>/dev/null || true

# === 3. Iniciar Dashboard ===
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ▶️ Iniciando Dashboard..."
nohup "$VENV_DIR/bin/python" "$PROJECT_ROOT/aura_dashboard.py" \
    > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > "$LOG_DIR/dashboard.pid"

sleep 2

if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Dashboard rodando em: http://127.0.0.1:8765"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Falha ao iniciar o Dashboard. Verifique: $LOG_DIR/dashboard.log"
fi

# === 4. Iniciar Sofia State Loop ===
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ▶️ Iniciando Sofia State Loop..."
nohup "$VENV_DIR/bin/python" "$PROJECT_ROOT/update_sofia_state.py" \
    > "$LOG_DIR/autonomy_loop.log" 2>&1 &
echo $! > "$LOG_DIR/autonomy_loop.pid"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Sofia State Loop iniciado"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Aura Fusion está VIVO"
echo "📊 Dashboard: http://127.0.0.1:8765"
echo "📁 Logs: $LOG_DIR"
echo "🛑 Para parar tudo: ./stop_aura_fusion.sh"
echo "════════════════════════════════════════════════════════════"
