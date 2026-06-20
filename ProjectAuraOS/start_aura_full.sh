#!/usr/bin/env bash
set -euo pipefail

PROJECT="$HOME/ProjectAuraOS"
FUSION="$PROJECT/fusion"
VENV="$FUSION/.venv"
LOG_DIR="$PROJECT/logs"
mkdir -p "$LOG_DIR"

echo "🚀 Iniciando Aura Fusion Completo (v5 - Robusto)..."

# Ativar venv
source "$VENV/bin/activate"

# Verificar se Flask está instalado
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️ Flask não encontrado no venv. Instalando..."
    pip install flask psutil --quiet
fi

# Parar processos antigos
pkill -f "aura_dashboard.py" 2>/dev/null || true
pkill -f "fusiond" 2>/dev/null || true

# 1. Iniciar fusiond (daemon principal)
echo "▶️ Iniciando fusiond..."
nohup python -m aura_fusion.fusiond --foreground > "$LOG_DIR/fusiond.log" 2>&1 &
echo $! > "$LOG_DIR/fusiond.pid"
sleep 4

# 2. Iniciar Dashboard (usando python do venv explicitamente)
echo "▶️ Iniciando Dashboard..."
nohup python "$PROJECT/aura_dashboard.py" > "$LOG_DIR/dashboard.log" 2>&1 &
DASH_PID=$!
echo $DASH_PID > "$LOG_DIR/dashboard.pid"

sleep 3

# Verificar se o dashboard subiu
if ps -p $DASH_PID > /dev/null; then
    echo "✅ Dashboard rodando em: http://127.0.0.1:8765"
else
    echo "❌ Falha ao iniciar o Dashboard. Verifique o log:"
    echo "   cat $LOG_DIR/dashboard.log"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Aura Fusion está rodando"
echo "📊 Dashboard: http://127.0.0.1:8765"
echo "📁 Logs: $LOG_DIR"
echo "🛑 Para parar tudo: pkill -f 'fusiond|dashboard'"
echo "════════════════════════════════════════════════════════════"
