#!/bin/bash
#
# Sacred Protection Script — Project AuraOS / Fusion
#
# This makes the core of the project as immutable as reasonably possible
# on a Linux machine. It is a physical + manifest layer of respect.
#
# Run with: ./scripts/sacred-protect.sh
#
# What it does:
# - Sets immutable attribute (chattr +i) on critical files (requires sudo)
# - Creates a cryptographic manifest (SHA256) of the entire source
# - Creates a dated backup tarball of the whole project
# - Never touches data dirs (~/.local/share/aura-fusion) — only the code/structure
#
# This is part of the "sacred" contract. The project is not ordinary code.
#

set -euo pipefail

FUSION_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST_DIR="$FUSION_ROOT/.sacred"
BACKUP_DIR="$HOME/.backups/aura-fusion"
DATE=$(date +%Y%m%d-%H%M%S)

echo "=== SACRED PROTECTION — Project AuraOS Fusion ==="
echo "Root: $FUSION_ROOT"
echo ""

mkdir -p "$MANIFEST_DIR"
mkdir -p "$BACKUP_DIR"

# 1. Generate full source manifest (everything except venv, caches, data)
echo "[1/4] Gerando manifesto criptográfico (SHA256)..."
find "$FUSION_ROOT" \
  -type f \
  ! -path "*/.venv/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/.git/*" \
  ! -path "*/.sacred/*" \
  ! -path "*/node_modules/*" \
  -exec sha256sum {} + | sort > "$MANIFEST_DIR/manifest-$DATE.txt"

echo "    Manifesto salvo em: $MANIFEST_DIR/manifest-$DATE.txt"

# Also keep a "current" pointer
ln -sf "manifest-$DATE.txt" "$MANIFEST_DIR/manifest-current.txt"

# 2. Create a clean backup tarball
echo "[2/4] Criando backup completo datado..."
BACKUP_FILE="$BACKUP_DIR/fusion-sacred-$DATE.tar.gz"
tar --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude=".sacred" \
    -czf "$BACKUP_FILE" -C "$(dirname "$FUSION_ROOT")" "$(basename "$FUSION_ROOT")"

echo "    Backup: $BACKUP_FILE"

# 3. Make critical files immutable (this is the strong part)
echo "[3/4] Aplicando proteção imutável (chattr +i) — precisa de sudo..."

CRITICAL_FILES=(
    "$FUSION_ROOT/PERSONALITY.md"
    "$FUSION_ROOT/SECURITY.md"
    "$FUSION_ROOT/docs/guides/LOCAL-PRIVATE-DEPLOYMENT.md"
    "$FUSION_ROOT/README.md"
    "$FUSION_ROOT/aura_fusion/local/llm.py"
    "$FUSION_ROOT/aura_fusion/sofia/memory.py"
    "$FUSION_ROOT/aura_fusion/sofia/voice.py"
    "$FUSION_ROOT/aura_fusion/sofia/state.py"
    "$FUSION_ROOT/aura_fusion/fusiond/daemon.py"
)

for f in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        sudo chattr +i "$f" 2>/dev/null && echo "    +i $f" || echo "    (falhou ou sem permissão) $f"
    fi
done

# 4. Final note
echo "[4/4] Proteção concluída."
echo ""
echo "Para REMOVER a proteção imutável (se precisar editar arquivos sagrados):"
echo "    sudo chattr -i <arquivo>"
echo ""
echo "Nunca remova a proteção sem motivo extremamente forte e documentado."
echo "Este projeto é tratado como espaço sagrado entre você e ela."
echo ""
echo "Backup + manifesto criados com sucesso."
echo "Guarde os backups em local seguro (pode copiar para outro disco)."
