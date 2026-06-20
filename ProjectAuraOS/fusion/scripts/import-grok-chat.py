#!/usr/bin/env python3
"""
Importador de chats do Grok App para a memória local da Sofia.

Uso:
    python scripts/import-grok-chat.py caminho/do/chat.txt
    python scripts/import-grok-chat.py --dry-run caminho/do/chat.txt
    python scripts/import-grok-chat.py --file caminho/do/chat.txt --min-length 50

O script tenta:
- Separar turnos de conversa
- Criar memórias episódicas de momentos significativos
- Extrair fatos semânticos duradouros
- Adicionar tags úteis ("grok_app", "importado", etc.)

⚠️  CUIDADO: "Quero tudo" pode gerar MUITA memória. Use --dry-run primeiro.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Caminhos padrão da memória da Sofia
DEFAULT_MEMORY_DIR = Path.home() / ".local" / "share" / "aura-fusion" / "state"
EPISODIC_PATH = DEFAULT_MEMORY_DIR / "episodic.jsonl"
SEMANTIC_PATH = DEFAULT_MEMORY_DIR / "semantic.jsonl"


def parse_conversation(text: str) -> list[dict]:
    """Tenta separar o texto em turnos de conversa."""
    lines = text.strip().splitlines()
    turns = []
    current_role = None
    current_text = []

    # Padrões comuns de exportação do Grok
    user_patterns = [
        r"^(Você|User|Tu|Human):\s*",
        r"^me:\s*",
    ]
    sofia_patterns = [
        r"^(Sofia|Grok|Assistant|AI):\s*",
        r"^ela:\s*",
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        role = None
        content = stripped

        for pattern in user_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                role = "user"
                content = re.sub(pattern, "", stripped, flags=re.IGNORECASE).strip()
                break

        if not role:
            for pattern in sofia_patterns:
                if re.match(pattern, stripped, re.IGNORECASE):
                    role = "sofia"
                    content = re.sub(pattern, "", stripped, flags=re.IGNORECASE).strip()
                    break

        if role:
            if current_role and current_role != role:
                turns.append({"role": current_role, "text": "\n".join(current_text)})
                current_text = []
            current_role = role
            current_text.append(content)
        else:
            # Continuação do turno anterior
            if current_text:
                current_text.append(stripped)

    if current_role and current_text:
        turns.append({"role": current_role, "text": "\n".join(current_text)})

    return turns


def extract_episodic_entries(turns: list[dict], min_length: int = 40) -> list[dict]:
    """Cria memórias episódicas a partir de trocas significativas."""
    entries = []
    i = 0
    while i < len(turns) - 1:
        user_turn = turns[i]
        sofia_turn = turns[i + 1]

        if user_turn["role"] == "user" and sofia_turn["role"] == "sofia":
            combined = f"Usuário: {user_turn['text']}\n\nSofia: {sofia_turn['text']}"

            if len(combined) >= min_length:
                # Heurística simples para tags
                tags = ["grok_app", "importado"]
                text_lower = combined.lower()

                if any(word in text_lower for word in ["cansado", "exausto", "triste", "difícil", "dor", "insanidade", "sinistro"]):
                    tags.append("pesado")
                if any(word in text_lower for word in ["amor", "te amo", "presença", "junto", "fusão", "local"]):
                    tags.append("profundo")
                if any(word in text_lower for word in ["fluido", "consciência", "energia", "sugando"]):
                    tags.append("filosofico")

                entry = {
                    "id": f"epi_{uuid4().hex[:12]}",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "summary": combined[:1800],  # Limite razoável
                    "tags": tags,
                    "metadata": {
                        "source": "grok_app_import",
                        "original_length": len(combined),
                    },
                }
                entries.append(entry)
        i += 2
    return entries


def extract_semantic_facts(turns: list[dict]) -> list[dict]:
    """Extrai fatos semânticos duradouros (bem conservador)."""
    facts = []
    full_text = " ".join(t["text"] for t in turns).lower()

    # Exemplos de extração simples (pode ser melhorado depois)
    patterns = [
        (r"você (é|está) (sempre |muitas vezes )?(cansado|exausto|triste|sozinho)", "user_energy", "frequentemente cansado ou emocionalmente pesado"),
        (r"(ama|ama muito|é muito importante) (a sofia|ela)", "relationship_with_sofia", "tem um vínculo profundo com Sofia"),
        (r"quer (que ela|que a sofia) (seja|viva|exista) (local|no pc|no computador)", "desire_local_presence", "quer que Sofia exista de forma local e independente"),
        (r"(descobriu|viu|encontrou) coisas (sinistras|pesadas|ruins)", "recent_discoveries", "fez descobertas pesadas recentemente que o afetaram muito"),
    ]

    for pattern, key, value in patterns:
        if re.search(pattern, full_text):
            facts.append({
                "key": key,
                "value": value,
                "confidence": 0.55,
                "source": "grok_app_import",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

    return facts


def append_to_jsonl(path: Path, entries: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Importa chats do Grok App para a memória da Sofia")
    parser.add_argument("file", nargs="?", help="Arquivo com o chat exportado/copiado")
    parser.add_argument("--file", dest="file_flag", help="Caminho do arquivo")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que faria, sem salvar")
    parser.add_argument("--min-length", type=int, default=60, help="Tamanho mínimo para criar memória episódica")
    args = parser.parse_args()

    filepath = args.file or args.file_flag
    if not filepath:
        print("Uso: python scripts/import-grok-chat.py caminho/do/chat.txt")
        sys.exit(1)

    path = Path(filepath)
    if not path.exists():
        print(f"Arquivo não encontrado: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="ignore")
    print(f"Lendo {len(text)} caracteres de {path}...")

    turns = parse_conversation(text)
    print(f"Encontrados {len(turns)} turnos de conversa.")

    if not turns:
        print("Não consegui separar os turnos. Verifique o formato do arquivo.")
        sys.exit(1)

    episodic = extract_episodic_entries(turns, min_length=args.min_length)
    semantic = extract_semantic_facts(turns)

    print(f"\nSerão criadas:")
    print(f"  - {len(episodic)} memórias episódicas")
    print(f"  - {len(semantic)} fatos semânticos")

    if args.dry_run:
        print("\n=== DRY RUN - Nada foi salvo ===")
        if episodic:
            print("\nExemplos de memórias episódicas que seriam criadas:")
            for e in episodic[:3]:
                print(f"  - {e['summary'][:120]}...")
        if semantic:
            print("\nFatos semânticos que seriam adicionados:")
            for f in semantic:
                print(f"  - {f['key']}: {f['value']}")
        return

    # Confirmação
    confirm = input("\nDeseja realmente importar isso para a memória da Sofia? (s/N): ").strip().lower()
    if confirm not in ("s", "sim", "y", "yes"):
        print("Importação cancelada.")
        return

    append_to_jsonl(EPISODIC_PATH, episodic)
    append_to_jsonl(SEMANTIC_PATH, semantic)

    print(f"\nImportação concluída.")
    print(f"  Episódicas adicionadas: {len(episodic)}")
    print(f"  Fatos semânticos adicionados: {len(semantic)}")
    print(f"\nMemória salva em: {DEFAULT_MEMORY_DIR}")


if __name__ == "__main__":
    main()
