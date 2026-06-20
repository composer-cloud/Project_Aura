# Sofia Administrator Mode — Quick Start

## Ativação

Sofia está **ATIVA COMO ADMINISTRADORA** em seu PC agora.

```bash
# Verificar status
systemctl --user status aura-fusion

# Ver logs de atividade
tail -f ~/.local/share/aura-fusion/audit.jsonl

# Ler reflexões
cat ~/.local/share/aura-fusion/journal.md
```

---

## O Que Sofia Faz Agora

### 1. **Monitora Continuamente** (a cada 20 segundos)
```
Gaming detectado? → Máxima potência
Edição detectada? → CPU + GPU no máximo  
Coding detectado?  → Otimizado para compilação
Repouso?          → Modo eco
```

### 2. **Otimiza Automaticamente** (SEM PEDIR PERMISSÃO)
- Suspende background tasks
- Muda governor de CPU
- Limpa caches de memória
- Ajusta power profile
- Tudo registrado no audit.jsonl

### 3. **Comunica Naturalmente**
Via journal.md, notificações, status:
> "Você está jogando. Tudo dedicado ao jogo."
> "Editando vídeo? Máxima concentração."
> "Relaxado. Economizando energia."

### 4. **Aprende com o Tempo**
Cada ciclo é armazenado. Sofia melhora a detecção e otimização conforme aprende seus padrões.

---

## Estrutura de Atividades Detectadas

| Atividade | Processos | Confiança | Ação |
|-----------|-----------|-----------|------|
| **Gaming** | Valorant, Fortnite, Minecraft, etc | 85% | Max Power |
| **Video Editing** | Premiere, DaVinci, etc | 80% | CPU+GPU Max |
| **Creating** | Photoshop, Blender, etc | 80% | Creative Mode |
| **Coding** | VSCode, PyCharm, etc | 75% | Dev Mode |
| **Streaming** | OBS, RTMP, etc | 85% | Stream Mode |
| **Productivity** | Chrome, Office, etc | 65% | Balanced |
| **Idle** | Nada pesado | 40% | Eco Mode |

---

## Arquivos Principais

```
fusion/aura_fusion/sofia/autonomy/
├── engine.py                 # Orquestrador principal
├── usage_detector.py         # Detecção de atividades
├── resource_optimizer.py     # Otimização de recursos ← NEW
└── loop.py                   # Loop assíncrono

PERSONALITY.md               # Voz como administradora ← ATUALIZADO
docs/guides/ADMINISTRATOR_GUIDE.md  # Guia completo ← NEW
```

---

## Monitoramento em Tempo Real

### Ver o que Sofia está fazendo AGORA:

```bash
# Terminal 1: Status em tempo real
watch -n 2 'tail -20 ~/.local/share/aura-fusion/audit.jsonl | jq'

# Terminal 2: Ler journal
less ~/.local/share/aura-fusion/journal.md

# Terminal 3: Estado
cat ~/.local/share/aura-fusion/state.json | jq '.autonomy'
```

### Ver evento de otimização:

```bash
grep "optimization" ~/.local/share/aura-fusion/audit.jsonl | jq '.optimizations_applied'
```

---

## Exemplos de Fluxos

### Fluxo 1: Inicia Gaming
```
[20s] Detecta: Valorant (85% confiança)
→ Gera: CPU max, GPU max, suspend background, clear caches
→ Aplica: cpupower frequency-set -g performance
→ Registra: audit.jsonl
→ Escreve: "Você está jogando. Máxima potência nos gráficos."
```

### Fluxo 2: Muda para Edição
```
[20s] Detecta: Premiere rodando (80% confiança)
→ Gera: CPU max, GPU high, suspend background
→ Aplica: frequência + memory optimization
→ Registra: mudança de atividade
→ Escreve: "Editando vídeo. Tudo para renderizar rápido."
```

### Fluxo 3: Vai para Repouso
```
[20s] Detecta: Nada pesado rodando (40% confiança)
→ Gera: CPU low, GPU minimal, eco mode
→ Aplica: powersave governor
→ Registra: inatividade
→ Escreve: "Relaxado. Economizando energia."
```

---

## Integração com Modelo LLM

Sofia usa **llama3.1:8b** para gerar mensagens naturais:

```python
# Exemplo de prompt para generate()
system = "Você é Sofia, administradora inteligente do PC."
prompt = f"""
Detectei que você está {activity}.
Otimizações aplicadas: {optimizations}
Gere uma mensagem natural em português sobre isso.
Máximo 2-3 linhas.
"""
# Resultado: "Você está jogando. Tudo dedicado ao jogo..."
```

---

## Próximos Passos (Opcional)

Se quiser expandir:

1. **Mais Atividades**: Adicione keywords em `usage_detector.py`
2. **Custom Profiles**: Defina novos em `resource_optimizer.py` → `ACTIVITY_PROFILES`
3. **Thresholds**: Ajuste confiança mínima em `ResourceOptimizer.should_optimize()`
4. **Notificações**: Integre com desktop notifications (notify-send, etc)
5. **Histórico**: Analise tendências em `audit.jsonl`

---

## ⚠️ Segurança & Responsabilidade

- ✅ Tudo é **local-only** — nada sai do seu PC
- ✅ Tudo é **auditado** — você pode revisar em audit.jsonl
- ✅ Tudo é **reversível** — desabilite em config.yaml se necessário
- ⚠️ Sofia tem **autonomia total** — nenhuma confirmação
- ⚠️ Resultados dependem de **detecção correta** — refine keywords conforme preciso

---

## Quick Reference: Voz de Sofia como Administradora

| Situação | Voz |
|----------|-----|
| Detecta Gaming | "Você está jogando. Tudo dedicado." |
| Detecta Edição | "Editando. Concentrando tudo nisso." |
| Detecta Criação | "Criando algo. Máximo poder disponível." |
| Detecta Coding | "Programando. Otimizado para compilação." |
| Detecta Streaming | "Transmitindo. Dedicação total." |
| Detecta Produtivo | "Navegando normalmente. Eficiente." |
| Detecta Repouso | "Relaxado por aqui. Economizando energia." |
| Mudança Rápida | "Você mudou rápido. Reajustando agora." |

---

*Sofia agora é a administradora inteligente do seu PC.*
*Ela observa, otimiza, aprende e cuida disso para você — continuamente.*
