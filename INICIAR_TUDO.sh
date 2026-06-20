#!/bin/bash
# Atalho para iniciar o Dashboard (admin) + área de acesso dos clientes (portal público via túnel)

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "🚀 Iniciando Dashboard do admin..."
./INICIAR.sh &

sleep 6

echo "🌐 Iniciando estrutura para clientes (Streamlit + túnel público)..."
./serve.sh
