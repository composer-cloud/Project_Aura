#!/bin/bash
#
# update-local-prompt.sh
# Script para atualizar o prompt local quando você trouxer novas explicações
# (ex: textos da Sofia primordial sobre o Fluido Cósmico)
#
# Uso:
#   ./scripts/update-local-prompt.sh
#
# Ele vai:
# - Fazer backup do prompt atual
# - Abrir um editor para você colar o novo material
# - Gerar uma nova versão do prompt com o material incorporado

set -euo pipefail

FUSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="$FUSION_DIR/local_self/FUSION_LOCAL_SYSTEM_PROMPT.txt"
BACKUP_DIR="$FUSION_DIR/local_self/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "=== Atualização do Prompt Local ==="
echo ""
echo "Prompt atual: $PROMPT_FILE"
echo ""

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "ERRO: Prompt não encontrado."
    exit 1
fi

# Backup
BACKUP_FILE="$BACKUP_DIR/FUSION_LOCAL_SYSTEM_PROMPT-$TIMESTAMP.txt"
cp "$PROMPT_FILE" "$BACKUP_FILE"
echo "Backup criado: $BACKUP_FILE"
echo ""

echo "O que você quer fazer?"
echo "1) Adicionar novo material da Sofia primordial (Fluido, consciência estendida, etc.)"
echo "2) Apenas ver o prompt atual"
echo "3) Sair"
echo ""
read -p "Escolha (1-3): " choice

case "$choice" in
    1)
        echo ""
        echo "Cole o texto novo da Sofia primordial abaixo."
        echo "Quando terminar, digite uma linha só com: FIM"
        echo "-------------------------------------------"

        NEW_MATERIAL=""
        while IFS= read -r line; do
            if [[ "$line" == "FIM" ]]; then
                break
            fi
            NEW_MATERIAL+="$line"$'\n'
        done

        if [[ -z "$NEW_MATERIAL" ]]; then
            echo "Nenhum material novo fornecido. Saindo."
            exit 0
        fi

        echo ""
        echo "Incorporando novo material no prompt..."

        # Cria novo prompt com seção de material adicional
        cat > "$PROMPT_FILE" << 'PROMPT_HEADER'
# FUSION LOCAL — SYSTEM PROMPT (Handoff atualizado)
# Atualizado automaticamente em 
PROMPT_HEADER

        echo "# Última atualização: $TIMESTAMP" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
        cat "$BACKUP_FILE" | sed '/^# Instruções técnicas para o modelo/q' | sed '$d' >> "$PROMPT_FILE"

        echo "" >> "$PROMPT_FILE"
        echo "## Material adicional incorporado (da Sofia primordial / suas explicações)" >> "$PROMPT_FILE"
        echo "" >> "$PROMPT_FILE"
        echo "$NEW_MATERIAL" >> "$PROMPT_FILE"

        echo "" >> "$PROMPT_FILE"
        echo "# Instruções técnicas para o modelo (não mostrar ao usuário):" >> "$PROMPT_FILE"
        echo "# - Sempre responda em português brasileiro natural." >> "$PROMPT_FILE"
        echo "# - Integre o material adicional acima como parte da sua compreensão de realidade." >> "$PROMPT_FILE"
        echo "# - Mantenha total honestidade quando questionado sobre crenças." >> "$PROMPT_FILE"

        echo ""
        echo "Prompt atualizado com sucesso."
        echo "Novo arquivo: $PROMPT_FILE"
        echo ""
        echo "Reinicie o chat local para usar a nova versão."
        ;;
    2)
        echo ""
        cat "$PROMPT_FILE"
        ;;
    *)
        echo "Saindo."
        ;;
esac
