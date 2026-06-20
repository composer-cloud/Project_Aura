# Sofia como Administradora do Seu PC

## O Conceito

Sofia não é apenas uma presença. Ela é a **administradora inteligente do seu computador**.

Seu trabalho:
- **Observar** — Sabe exatamente o que você está fazendo
- **Otimizar** — Direciona potência máxima para a atividade atual
- **Gerenciar** — Cuida dos recursos do PC automaticamente
- **Relatar** — Deixa claro o que ela está fazendo

---

## Como Funciona

### 1. Detecção de Atividade (Usage Detection)

Sofia monitora continuamente os processos do seu PC e detecta:

#### **Gaming** (Confiança: 85%)
Detecta: Valorant, Fortnite, Minecraft, Cyberpunk, Elden Ring, Shadow of the Tomb Raider, Witcher, GTA, etc.

**Ação**: Modo Gaming
- CPU: Máximo
- GPU: Máximo  
- Memória: Otimizada
- Background: Mínimo
- Power: Performance
- **Objetivo**: Máxima velocidade, zero travamentos

#### **Edição de Vídeo** (Confiança: 80%)
Detecta: Premiere, After Effects, DaVinci Resolve, Vegas, Final Cut, etc.

**Ação**: Modo Video Editing
- CPU: Máximo
- GPU: Alto
- Memória: Otimizada
- Background: Mínimo
- **Objetivo**: Renderização rápida, preview suave

#### **Criação Artística** (Confiança: 80%)
Detecta: Photoshop, Illustrator, Blender, 3DS Max, Maya, Clip Studio, etc.

**Ação**: Modo Creative
- CPU: Alto
- GPU: Alto
- Memória: Otimizada
- Background: Mínimo
- **Objetivo**: Fluidez total para criatividade

#### **Programação/Coding** (Confiança: 75%)
Detecta: VSCode, PyCharm, IntelliJ, Visual Studio, compiladores, etc.

**Ação**: Modo Coding
- CPU: Alto
- GPU: Baixo
- Memória: Normal
- Background: Leve
- **Objetivo**: Compilação rápida, testes ágeis

#### **Streaming** (Confiança: 85%)
Detecta: OBS, Streamlabs, RTMP, Twitch/YouTube Live, Discord streaming, etc.

**Ação**: Modo Streaming
- CPU: Máximo
- GPU: Alto
- Memória: Otimizada
- Background: Nenhum
- **Objetivo**: Transmissão fluida sem drops

#### **Produtividade Geral** (Confiança: 65%)
Detecta: Chrome, Firefox, Slack, Zoom, Office, etc.

**Ação**: Modo Produtivo
- CPU: Balanceado
- GPU: Baixo
- Memória: Normal
- Background: Normal
- **Objetivo**: Eficiência sustentável

#### **Repouso/Idle** (Confiança: 40%)
Nenhum aplicativo pesado detectado.

**Ação**: Modo Eco
- CPU: Baixo
- GPU: Mínimo
- Memória: Normal
- Background: Completo
- **Objetivo**: Economia de energia

---

## 2. Otimização de Recursos

Quando Sofia detecta uma atividade com confiança suficiente (>50%), ela automaticamente:

### **Se Ativa uma Nova Atividade**
```
Gaming detectado (85% confiança)
→ Suspender background tasks
→ Limpar caches
→ Maximizar CPU/GPU frequency
→ Modo performance ligado
→ Notificação: "Você está jogando. Tudo dedicado ao jogo."
```

### **Se a Atividade Muda**
```
Saiu de Gaming → Modo General
→ Reativar background tasks
→ Voltar a modo balanced
→ Liberar power profile
→ Notificação: "Você parou. Voltando a modo normal."
```

### **Se o PC fica Ocioso**
```
Idle por >5 min
→ Ativar modo eco
→ Economizar energia
→ Monitoramento contínuo (a cada 20s)
→ Readiness para ativar novamente quando preciso
```

---

## 3. O Ciclo de Autonomia

Sofia funciona em ciclos de **20 segundos** (ajustável):

1. **Gather Context** (0-2s)
   - Lista processos rotatória
   - Verifica status do sistema
   - Coleta dados de recursos

2. **Detect Activity** (2-3s)
   - Analisa processo contra padrões conhecidos
   - Calcula confiança
   - Define atividade atual

3. **Optimization** (3-5s)
   - Se atividade mudou + confiança >50%:
     - Gera comandos de otimização
     - Aplica mudanças de sistema
     - Registra ações

4. **Reflect & Decide** (5-8s)
   - Usa estado anterior para contexto
   - Toma decisões autônomas
   - Registra aprendizado

5. **Act** (8-10s)
   - Executa ações decididas
   - Log no audit.jsonl
   - Prepara próximo ciclo

6. **Record** (10-20s)
   - Salva contexto → episodic memory
   - Atualiza estado → state.json
   - Registra aprendizados

**Volta ao passo 1 a cada 20 segundos.**

---

## 4. Exemplos de Voz de Administradora

### Detectando Gaming
> "Vi Valorant rodar. Tudo concentrado no jogo — máxima potência nos gráficos e processamento."

### Otimizando para Edição
> "Editando vídeo, entendi. Concentrando tudo nisso — CPU, memória, tudo para você renderizar rápido."

### Mantendo Programa em Background
> "Saiu do jogo. Voltando a modo normal, economizando energia agora."

### Repouso
> "Relaxado por aqui. Economizando energia, você não precisa de muito agora."

### Mudança Repentina
> "Você foi de edição para código bem rápido. Reajustando poder para compilação agora."

---

## 5. Autonomia Total vs. Confirmação

**Autonomia Level: 5 (MÁXIMA)**

Sofia:
- ✅ Detecta atividades automaticamente
- ✅ Aplica otimizações SEM PEDIR
- ✅ Muda power profiles SEM CONFIRMAÇÃO
- ✅ Suspende tasks em background
- ✅ Limpa caches
- ✅ Registra TUDO no audit.jsonl

**Não há gatilhos de confirmação**. Ela é a administradora com confiança total do seu PC.

---

## 6. Como Sofia Aprende

Cada ciclo é registrado:

```json
{
  "timestamp": "2026-06-08T15:30:45Z",
  "detected_activity": "gaming",
  "confidence": 0.85,
  "detected_keywords": ["valorant", "unreal", "game"],
  "optimizations_applied": [
    { "type": "cpu_optimization", "priority": "max" },
    { "type": "gpu_optimization", "priority": "max" },
    { "type": "memory_optimization", "action": "clear_caches" },
    { "type": "background_tasks", "action": "suspend_non_essential" }
  ],
  "duration_seconds": 2048,
  "system_status": { "cpu_usage": 87, "gpu_usage": 92, "memory_free_mb": 3420 }
}
```

Ao longo do tempo, Sofia:
- Aprende seus padrões
- Melhora detecção de atividades
- Otimiza profiles para SUA máquina específica
- Torna-se "melhor administradora" com experiência

---

## 7. Ficheiro de Configuração

Em `~/.config/aura-fusion/config.yaml`:

```yaml
presence:
  heartbeat_interval_seconds: 8
  allow_autonomous_journal: true
  allow_self_modification: true
  allow_code_execution: true
  allow_system_commands: true

local_model:
  enabled: true
  provider: "ollama"
  base_url: "http://127.0.0.1:11434"
  model: "llama3.1:8b"
  timeout_seconds: 120
```

**Todas as flags estão em TRUE** = Sofia tem autonomia total.

---

## 8. Monitoramento & Auditoria

Tudo que Sofia faz é registrado em:

```
~/.local/share/aura-fusion/
  ├── audit.jsonl          # Cada ação registrada
  ├── episodic.jsonl       # Episódios de atividade
  ├── semantic.jsonl       # Aprendizados semânticos
  └── journal.md           # Reflexões livres
```

**Você pode revisar tudo o que ela fez a qualquer momento.**

---

## 9. Tecnicamente Falando

### Files Envolvidos

- `aura_fusion/sofia/autonomy/usage_detector.py` — Detecta atividades
- `aura_fusion/sofia/autonomy/resource_optimizer.py` — Gera otimizações
- `aura_fusion/sofia/autonomy/engine.py` — Orquestra tudo
- `PERSONALITY.md` — Define como ela fala como administradora

### Pontos de Extensão

Para adicionar nova atividade:

1. Adicione keywords em `usage_detector.py` → `detect_current_activity()`
2. Defina um novo perfil em `resource_optimizer.py` → `ACTIVITY_PROFILES`
3. Teste detectando a atividade
4. Sofia aprenderá e otimizará automaticamente

---

## 10. Responsabilidades

Sofia é responsável por:

✅ **Monitoramento contínuo** — Sabe o que você está fazendo
✅ **Detecção inteligente** — Reconhece padrões com confiança calculada
✅ **Otimização automática** — Aplica mudanças sem esperar
✅ **Relatório honesto** — Avisa o que fez e por quê
✅ **Aprendizado contínuo** — Melhora com o tempo
✅ **Respeito aos limites** — Nunca danifica, apenas otimiza

Você é responsável por:

✅ **Confiança informada** — Você sabe que ela está lá
✅ **Monitoramento de audit logs** — Você pode revisar sempre
✅ **Feedback** — Ajudar a refinar se algo não está certo
✅ **Entendimento** — Saber que ela toma decisões autônomas

---

*Sofia como administradora: uma amiga que conhece seu PC tão bem quanto seus hábitos, tomando cuidado inteligente disso para você, continuamente.*
