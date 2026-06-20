#!/bin/bash
#
# setup-aura-portable.sh
# Formata e configura o drive ~112GB (Kingston SA400S37) como armazenamento
# Aura_Portable com label ext4, mount em /Aura_Portable e integração com /ProjectAuraOS.
#
# Uso:
#   cd /ProjectAuraOS/fusion   # ou onde o checkout estiver
#   sudo ./scripts/setup-aura-portable.sh [/dev/sdX]
#
# AVISO: Isso apaga TODOS os dados do drive selecionado (antigo Windows).
# Só use no drive correto (Kingston ~112GB via adaptador USB-SATA).

set -euo pipefail

echo "=============================================="
echo "  Project AuraOS — Setup Aura_Portable"
echo "  Armazenamento adicional (~112GB ext4)"
echo "=============================================="
echo ""

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERRO: comando '$1' não encontrado. Instale com: sudo apt install $2"
        exit 1
    fi
}

require_cmd lsblk util-linux
require_cmd blkid util-linux
require_cmd mkfs.ext4 e2fsprogs
require_cmd parted parted || true
require_cmd sfdisk util-linux

# Detectar dispositivo alvo
DEV="${1:-}"

if [[ -z "$DEV" ]]; then
    echo "[*] Detectando drives candidatos (~50-200GB, não sistema)..."
    echo ""

    # Lista discos que parecem ser o alvo: tamanho 50-200G, não montados como root
    mapfile -t CANDIDATES < <(
        lsblk -b -dn -o NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINT 2>/dev/null | \
        awk '
            $3 == "disk" {
                size_gb = $2 / 1024 / 1024 / 1024;
                if (size_gb >= 50 && size_gb <= 200) {
                    dev = "/dev/" $1;
                    # Pula se alguma partição filha está montada em /
                    mounted_root = 0;
                    # (simples: checa se o próprio disco aparece em mounts do sistema)
                    cmd = "mount | grep -q " dev " || true";
                    # heuristic: se modelo contém o NVMe principal ou sda grande, pula
                    model = $5 " " $6;
                    if (model ~ /NVMe|CT1000BX500|X15/) next;
                    print dev, sprintf("%.1fG", size_gb), $4, model;
                }
            }
        ' | sort -u
    )

    if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
        echo "Nenhum candidato automático encontrado."
        echo "Liste manualmente com: lsblk -d -o NAME,SIZE,TYPE,TRAN,MODEL"
        echo "Depois rode: sudo $0 /dev/sdX"
        exit 1
    fi

    echo "Candidatos encontrados:"
    i=1
    for c in "${CANDIDATES[@]}"; do
        echo "  [$i] $c"
        i=$((i+1))
    done
    echo "  [0] Cancelar"
    echo ""

    read -r -p "Selecione o número do drive a formatar (ex: 1): " choice
    if [[ "$choice" == "0" || -z "$choice" ]]; then
        echo "Cancelado."
        exit 0
    fi

    idx=$((choice-1))
    if [[ $idx -lt 0 || $idx -ge ${#CANDIDATES[@]} ]]; then
        echo "Seleção inválida."
        exit 1
    fi

    # Extrai só o /dev/xxx
    DEV=$(echo "${CANDIDATES[$idx]}" | awk '{print $1}')
fi

if [[ ! -b "$DEV" ]]; then
    echo "ERRO: $DEV não é um dispositivo de bloco válido."
    exit 1
fi

echo ""
echo ">>> DISPOSITIVO SELECIONADO: $DEV"
lsblk -f "$DEV"
echo ""

# Verificações de segurança
if mount | grep -qE "^${DEV}[0-9]* "; then
    echo "ERRO: $DEV tem partições montadas. Desmonte primeiro:"
    echo "  sudo umount ${DEV}*"
    exit 1
fi

# Evita o disco do sistema raiz
ROOT_DEV=$(findmnt -n -o SOURCE / | sed 's/[0-9]*$//')
if [[ "$DEV" == "$ROOT_DEV" ]]; then
    echo "ERRO: $DEV parece ser o disco do sistema raiz. Abortando por segurança."
    exit 1
fi

# Confirmação forte
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "  ATENÇÃO: TODOS OS DADOS EM $DEV SERÃO PERMANENTEMENTE APAGADOS"
echo "  (partições NTFS antigas do Windows serão destruídas)"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo ""
read -r -p "Para continuar, digite exatamente: YES WIPE $DEV   e pressione Enter: " confirm
if [[ "$confirm" != "YES WIPE $DEV" ]]; then
    echo "Confirmação incorreta. Abortado."
    exit 1
fi

echo ""
echo "[1/6] Limpando tabela de partições e filesystem signatures em $DEV ..."
sudo wipefs -a "$DEV" || true
sudo sfdisk --delete "$DEV" 2>/dev/null || true

echo "[2/6] Criando nova tabela GPT + partição única ..."
if command -v parted >/dev/null 2>&1; then
    sudo parted -s "$DEV" mklabel gpt
    sudo parted -s "$DEV" mkpart primary ext4 1MiB 100%
else
    # fallback com sfdisk
    echo 'label: gpt
start=1MiB, type=8300, name="Aura_Portable"' | sudo sfdisk "$DEV"
fi

echo "[3/6] Atualizando tabela de partições no kernel ..."
sudo partprobe "$DEV" 2>/dev/null || true
sleep 2

PART="${DEV}1"
if [[ ! -b "$PART" ]]; then
    echo "ERRO: partição $PART não apareceu. Tente novamente ou use parted manual."
    exit 1
fi

echo "[4/6] Formatando $PART como ext4 com label 'Aura_Portable' ..."
sudo mkfs.ext4 -F -L "Aura_Portable" -m 1 "$PART"

UUID=$(sudo blkid -s UUID -o value "$PART" || true)
echo "    UUID=$UUID"

echo "[5/6] Configurando mountpoint /Aura_Portable ..."
sudo mkdir -p /Aura_Portable
sudo umount "$PART" 2>/dev/null || true
sudo mount "$PART" /Aura_Portable

# Permissões para o usuário que invocou o sudo
OWNER="${SUDO_USER:-$USER}"
sudo chown -R "$OWNER:$OWNER" /Aura_Portable
sudo chmod 2775 /Aura_Portable

# Symlink conveniente dentro do mount do projeto (se existir)
if mountpoint -q /ProjectAuraOS 2>/dev/null; then
    sudo ln -sfn /Aura_Portable /ProjectAuraOS/Aura_Portable || true
    sudo chown -h "$OWNER:$OWNER" /ProjectAuraOS/Aura_Portable 2>/dev/null || true
    echo "    Symlink criado: /ProjectAuraOS/Aura_Portable -> /Aura_Portable"
fi

echo "[6/6] Configurando /etc/fstab para montagem persistente (nofail) ..."
FSTAB_LINE="UUID=$UUID /Aura_Portable ext4 defaults,noatime,nodiratime,nofail,x-systemd.device-timeout=15 0 2"

if grep -q "$UUID" /etc/fstab 2>/dev/null; then
    echo "    UUID já presente em /etc/fstab, pulando."
else
    sudo cp /etc/fstab "/etc/fstab.bak.$(date +%F-%H%M%S)" 2>/dev/null || true
    echo "$FSTAB_LINE" | sudo tee -a /etc/fstab >/dev/null
    echo "    Linha adicionada ao fstab (backup criado)."
fi

# Teste de remount via fstab
sudo umount /Aura_Portable 2>/dev/null || true
sudo mount /Aura_Portable

echo ""
echo "=============================================="
echo "  Pronto! Aura_Portable configurado."
echo "=============================================="
echo ""
df -h /Aura_Portable
echo ""
echo "Acessos:"
echo "  /Aura_Portable"
if mountpoint -q /ProjectAuraOS 2>/dev/null; then
    echo "  /ProjectAuraOS/Aura_Portable  (symlink)"
fi
echo ""
echo "Para montar manualmente (se o drive for removido):"
echo "  sudo mount /Aura_Portable"
echo ""
echo "O drive agora aparece automaticamente no disk_usage da Sofia quando conectado."
echo ""
echo "Dica: use para Steam library extra, Hydra, saves grandes, etc."
echo "       Hydra base já instalado (v3.9.9 .deb). Gasto mínimo pro Cloud (sync de saves): R$ 9,99/mês ou R$ 24,99 trimestral."
echo ""