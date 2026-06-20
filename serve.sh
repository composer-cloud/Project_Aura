#!/usr/bin/env bash
# Sobe o dashboard + túnel público para o Portal do Cliente.
# Uso: ./serve.sh

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=8501
LOG_DIR="$DIR/.logs"
mkdir -p "$LOG_DIR"

STREAMLIT_BIN="${STREAMLIT_BIN:-streamlit}"
CLOUDFLARED_BIN="${CLOUDFLARED_BIN:-cloudflared}"

if ! command -v "$STREAMLIT_BIN" >/dev/null 2>&1; then
  echo "Erro: streamlit não encontrado. Rode: pip install -r requirements.txt"
  exit 1
fi

if ! command -v "$CLOUDFLARED_BIN" >/dev/null 2>&1; then
  echo "Erro: cloudflared não encontrado."
  echo "Instale em ~/.local/bin ou defina CLOUDFLARED_BIN=/caminho/cloudflared"
  exit 1
fi

is_streamlit_up() {
  curl -fsS "http://127.0.0.1:${PORT}/_stcore/health" >/dev/null 2>&1
}

start_streamlit() {
  if is_streamlit_up; then
    echo "✓ Streamlit já está rodando na porta ${PORT}"
    return
  fi

  echo "→ Iniciando Streamlit na porta ${PORT}..."
  nohup "$STREAMLIT_BIN" run app.py \
    --server.port "$PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    >"$LOG_DIR/streamlit.log" 2>&1 &

  for _ in $(seq 1 30); do
    if is_streamlit_up; then
      echo "✓ Streamlit online"
      return
    fi
    sleep 1
  done

  echo "Erro: Streamlit não respondeu a tempo. Veja $LOG_DIR/streamlit.log"
  exit 1
}

save_public_url() {
  local url="$1"
  python3 - "$url" <<'PY'
import sqlite3
import sys

url = sys.argv[1].rstrip("/")
db = "isopor_parceiro.db"
conn = sqlite3.connect(db)
conn.execute(
    "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
    ("public_base_url", url),
)
conn.commit()
conn.close()
print(f"✓ URL pública salva no banco: {url}")
PY
}

start_tunnel() {
  if pgrep -f "cloudflared tunnel --url http://127.0.0.1:${PORT}" >/dev/null 2>&1; then
    echo "✓ Túnel Cloudflare já está ativo"
    if [[ -f "$LOG_DIR/tunnel.url" ]]; then
      cat "$LOG_DIR/tunnel.url"
      return
    fi
  fi

  echo "→ Abrindo túnel público (Cloudflare)..."
  : >"$LOG_DIR/tunnel.log"

  nohup "$CLOUDFLARED_BIN" tunnel --url "http://127.0.0.1:${PORT}" \
    >"$LOG_DIR/tunnel.log" 2>&1 &

  local public_url=""
  for _ in $(seq 1 45); do
    public_url="$(grep -Eo 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOG_DIR/tunnel.log" | head -1 || true)"
    if [[ -n "$public_url" ]]; then
      break
    fi
    sleep 1
  done

  if [[ -z "$public_url" ]]; then
    echo "Erro: não consegui obter a URL pública. Veja $LOG_DIR/tunnel.log"
    exit 1
  fi

  echo "$public_url" >"$LOG_DIR/tunnel.url"
  save_public_url "$public_url"
  echo ""
  echo "=============================================="
  echo "  Portal do Cliente ONLINE"
  echo "  URL pública: $public_url"
  echo "  Exemplo:      $public_url/?view=cliente&id=1"
  echo "  Logs:         $LOG_DIR/"
  echo "=============================================="
}

start_streamlit
start_tunnel