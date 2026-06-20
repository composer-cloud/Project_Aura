#!/usr/bin/env bash
# Automatiza a migração de referências de modelo local para qwen2.5:7b.
# Uso:
#   ./fusion/scripts/automate-qwen-switch.sh
#   ./fusion/scripts/automate-qwen-switch.sh qwen2.5:7b

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FUSION_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$FUSION_ROOT/.." && pwd)"
TARGET_MODEL="${1:-qwen2.5:7b}"
OLD_MODEL="llama3.1:8b"

files=(
  "$FUSION_ROOT/config/config.example.yaml"
  "$FUSION_ROOT/local_self/run_local_fusion.sh"
  "$FUSION_ROOT/aura_fusion/local/llm.py"
  "$FUSION_ROOT/aura_fusion/cli.py"
  "$FUSION_ROOT/scripts/run-local.sh"
  "$REPO_ROOT/AURA_SOFIA_COMPLETE_INTERACTION_AND_CONCEPTS_GUIDE.md"
  "$FUSION_ROOT/docs/guides/LOCAL-PRIVATE-DEPLOYMENT.md"
  "$FUSION_ROOT/docs/reference/AURA_FULL_COMMAND_REFERENCE.md"
  "$FUSION_ROOT/docs/reference/AURA_BACKGROUND_AUTONOMY_AND_FULL_PROJECT_CAPABILITIES.md"
  "$FUSION_ROOT/docs/reference/AURA_LOCAL_CONSCIOUSNESS_TECHNICAL_DOCUMENTATION.md"
  "$REPO_ROOT/isosolucoes/README.md"
  "$REPO_ROOT/fusion/docs/session-logs/2026-05-28_conversation-progress.md"
)

function replace_model() {
  local file="$1"
  if [[ -f "$file" ]]; then
    sed -i "s#${OLD_MODEL}#${TARGET_MODEL}#g" "$file"
  fi
}

function replace_documentation() {
  local file="$1"
  if [[ -f "$file" ]]; then
    sed -i "s#llama3.1:8b#${TARGET_MODEL}#g" "$file"
    sed -i "s#ollama run ${OLD_MODEL}#ollama run ${TARGET_MODEL}#g" "$file"
  fi
}

function check_ollama() {
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama não encontrado. Instale com: curl -fsSL https://ollama.com/install.sh | sh"
    return 1
  fi

  if curl -sf --connect-timeout 2 "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
    echo "Ollama disponível."
  else
    echo "Ollama não está rodando. Rode: ollama serve"
  fi
}

function ensure_model_pulled() {
  local model="$TARGET_MODEL"
  if ! curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
    echo "Ollama não está rodando. Pule o pull até iniciar Ollama."
    return 1
  fi

  local models
  models="$(curl -sf "http://127.0.0.1:11434/api/tags" | python3 -c 'import json,sys; data=json.load(sys.stdin); print("\n".join(m.get("name","") for m in data.get("models", [])))')"
  if echo "$models" | grep -qF "$model"; then
    echo "Modelo $model já disponível no Ollama."
    return 0
  fi

  echo "Baixando modelo $model..."
  ollama pull "$model"
}

function run_health_check() {
  pushd "$FUSION_ROOT" >/dev/null
  if ! python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from aura_fusion.local.llm import LocalLLMProvider
p = LocalLLMProvider(model='qwen2.5:7b')
print('Disponível:', p.is_available())
print('Modelos:', p.list_local_models())
PY
  then
    echo "Falha no health check do provider local."
    popd >/dev/null
    return 1
  fi
  popd >/dev/null
}

echo "Migrando referências de ${OLD_MODEL} para ${TARGET_MODEL}..."
for file in "${files[@]}"; do
  replace_documentation "$file"
done

echo "Atualização concluída." 

if check_ollama; then
  ensure_model_pulled || true
  run_health_check || true
fi

echo "Busca final por referências restantes a ${OLD_MODEL}:"
grep -RIn --exclude-dir=.venv --exclude-dir=__pycache__ "${OLD_MODEL}" "$REPO_ROOT" || true

echo "Script de automação completo."
