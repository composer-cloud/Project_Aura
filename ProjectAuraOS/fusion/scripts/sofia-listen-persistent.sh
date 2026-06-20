#!/usr/bin/env bash
set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION="sofia-listen"

cd "$FUSION_DIR"

if command -v tmux >/dev/null 2>&1; then
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Sessão tmux '$SESSION' já está rodando."
    exit 0
  fi

  echo "Iniciando Sofia Listen em tmux session '$SESSION'..."
  tmux new-session -d -s "$SESSION" "source '$FUSION_DIR/.venv/bin/activate' && exec '$FUSION_DIR/bin/sofia' listen"
  echo "Sessão tmux criada. Use: tmux attach -t $SESSION"
  exit 0
fi

echo "tmux não encontrado. Executando Sofia Listen no foreground..."
source "$FUSION_DIR/.venv/bin/activate"
exec "$FUSION_DIR/bin/sofia" listen
