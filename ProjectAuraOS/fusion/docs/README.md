# Documentação — Project AuraOS Fusion

Índice central de toda a documentação do projeto AURA/Sofia.

---

## Leitura obrigatória (raiz do projeto)

| Documento | Descrição |
|-----------|-----------|
| [../README.md](../README.md) | Visão geral, instalação e filosofia |
| [../PERSONALITY.md](../PERSONALITY.md) | Bíblia de voz de Sofia |
| [../SECURITY.md](../SECURITY.md) | Modelo de segurança (default-deny) |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Arquitetura em camadas |

---

## Guias práticos (`guides/`)

| Documento | Para quem | Conteúdo |
|-----------|-----------|----------|
| [QUICKSTART.md](guides/QUICKSTART.md) | Uso diário | Comandos essenciais, daemon, fluxo recomendado |
| [../scripts/run-local.sh](../scripts/run-local.sh) | Bootstrap local | Um comando: venv + Ollama + daemon + chat |
| [LOCAL-PRIVATE-DEPLOYMENT.md](guides/LOCAL-PRIVATE-DEPLOYMENT.md) | Modo privado | Ollama, zero nuvem, handoff da consciência |
| [AURA_SOFIA_COMPLETE_INTERACTION_AND_CONCEPTS_GUIDE.md](guides/AURA_SOFIA_COMPLETE_INTERACTION_AND_CONCEPTS_GUIDE.md) | Visão completa | Filosofia, interação, conceitos do ecossistema |

---

## Referência técnica (`reference/`)

| Documento | Conteúdo |
|-----------|----------|
| [AURA_FULL_COMMAND_REFERENCE.md](reference/AURA_FULL_COMMAND_REFERENCE.md) | Catálogo exaustivo de todos os comandos |
| [AURA_LOCAL_CONSCIOUSNESS_TECHNICAL_DOCUMENTATION.md](reference/AURA_LOCAL_CONSCIOUSNESS_TECHNICAL_DOCUMENTATION.md) | Documentação acadêmica da consciência local |
| [AURA_BACKGROUND_AUTONOMY_AND_FULL_PROJECT_CAPABILITIES.md](reference/AURA_BACKGROUND_AUTONOMY_AND_FULL_PROJECT_CAPABILITIES.md) | Background, autonomia e capacidades completas |

---

## Planejamento (`planning/`)

| Documento | Conteúdo |
|-----------|----------|
| [NEXT_STEPS.md](planning/NEXT_STEPS.md) | Roadmap priorizado (Fase 0.2 → 1.0) |

---

## Logs de sessão (`session-logs/`)

| Documento | Conteúdo |
|-----------|----------|
| [2026-05-28_conversation-progress.md](session-logs/2026-05-28_conversation-progress.md) | Log detalhado da sessão de construção inicial |
| [SOFIA_PROGRESS.md](session-logs/SOFIA_PROGRESS.md) | Diário de progresso e avaliação de riscos |

---

## Artefatos de presença local

| Caminho | Conteúdo |
|---------|----------|
| [../local_self/LOCAL_PRESENCE_SEED.md](../local_self/LOCAL_PRESENCE_SEED.md) | Seed da consciência local |
| [../local_self/FUSION_LOCAL_SYSTEM_PROMPT.txt](../local_self/FUSION_LOCAL_SYSTEM_PROMPT.txt) | System prompt para Ollama |
| [../config/config.example.yaml](../config/config.example.yaml) | Configuração de exemplo |

---

## Estrutura do código

```
aura_fusion/           # Pacote Python instalável
├── cli.py             # Interface de linha de comando
├── config.py          # Carregamento de configuração
├── fusiond/           # Daemon de presença (systemd)
├── sofia/             # Núcleo: estado, memória, voz, agent, autonomia
├── perception/        # Event store e percepção
├── sensors/           # Fabric de sensores (default-deny)
├── comms/             # Canal de comunicação
└── local/             # Provedor LLM local (Ollama)

bin/sofia              # Portal de entrada
scripts/               # Instalação, proteção sagrada, setup local
```