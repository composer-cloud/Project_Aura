#!/bin/bash
# Launcher for IsoCanal (IsoSoluções)
# Usage: ./scripts/launch_isocanal.sh

set -e

echo "=== IsoCanal — Inteligência de Canais e Leads (IsoSoluções) ==="
echo "Foco: identificação + auto-promoção value-first (sem propaganda incômoda)"
echo ""

cd "$(dirname "$0")/.."

# Check for streamlit
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Streamlit não encontrado. Instalando..."
    pip install streamlit pyyaml httpx --quiet
fi

# Check Ollama (soft warning)
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Aviso: Ollama não parece estar rodando em localhost:11434."
    echo "   A análise com IA local vai usar fallback (ainda útil, mas menos poderoso)."
    echo "   Rode 'ollama serve' + 'ollama run qwen2.5:7b' (ou modelo de sua preferência) em outra aba."
    echo ""
fi

echo "Abrindo IsoCanal em http://localhost:8502 ..."
echo "(Use Ctrl+C para parar)"
echo ""

streamlit run app/streamlit_app.py --server.port 8502 --server.headless true
