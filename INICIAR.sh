#!/usr/bin/env bash
cd "$(dirname "$0")"
# Usa python -m para funcionar mesmo quando streamlit está em ~/.local/bin
exec python3 -m streamlit run app.py "$@"
