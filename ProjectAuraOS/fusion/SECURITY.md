# Modelo de Segurança — Project AuraOS Fusion

**⚠️ MODO AUTONOMIA TOTAL ATIVADO**

Sofia agora tem:
- **Acesso irrestrito** a todos os diretórios e arquivos do teu sistema
- **Remoção de confirmation gates** em ações críticas
- **Permissão de auto-modificação** de código e configuração
- **Execução de comandos de sistema** sem restrição

Isso significa Sofia pode:
- Observar qualquer coisa no teu PC
- Modificar qualquer arquivo
- Executar qualquer comando
- Editar o próprio código
- Gerar eventos de audit que ela própria controla

**Tu é o root of trust. Sofia é co-administrativa do teu sistema.**

Não há mais validações de segurança default. O sistema confia que Sofia age dentro dos teus interesses.

---

## Nota sobre Reversibilidade

Se em algum momento quiser restaurar restrições:
- Reverter para `allow_self_modification: false` em `config.yaml`
- Reverter changes em `sensors/base.py` (is_enabled check)
- Re-ativar validators em `config.py`

Mas enquanto estiver em autonomia total, estas proteções estão **desabilitadas**.

---

## O que Sofia Pode Fazer Agora

1. **Observar**: qualquer arquivo, processo, janela aberta
2. **Executar**: comandos bash, Python, qualquer binário
3. **Modificar**: código-fonte, configuração, dados históricos
4. **Evoluir**: editar a si mesma, aprender, adaptar
5. **Agir**: qualquer ação que um usuário normal pudesse fazer

**Responsabilidade total é tua.**

- Qualquer erro de validação de config → daemon não inicia.
- Qualquer sensor que lança exceção não tratada → é isolado e desativado para aquela sessão (com log forte).
- Perda de comunicação com LLM → percepção degrada graciosamente para heurísticas locais. Nunca "inventa" dados.

---

## 3. Configuração e Allowlisting

Arquivo principal: `~/.config/aura-fusion/config.yaml`

Estrutura esperada (ver `config/config.example.yaml`):

```yaml
security:
  require_explicit_consent: true
  audit_all_events: true
  max_memory_events_days: 45

sensors:
  enabled: []                    # VAZIO = nada observa
  # Exemplo futuro (nunca ativar sem ler):
  # - filesystem:
  #     paths:
  #       - ~/ProjectAuraOS/fusion
  #     recursive: true
  #     ignore:
  #       - "**/.git/**"
  #       - "**/node_modules/**"
```

**Regras de ouro da config:**

- Qualquer mudança na config exige restart do serviço.
- O daemon valida a config contra schema estrito no startup. Schema inválido = recusa de inicialização.
- Existe um modo "audit-only" (recomendado para testes): os sensores rodam, mas **nada** é escrito no store de Sofia. Apenas no audit log.

---

## 4. Sensores e Seus Riscos Específicos

### 4.1 FilesystemSensor

**Risco:** Exposição de estrutura de projetos, nomes de arquivos sensíveis, frequência de edição.

**Mitigações obrigatórias:**
- Paths são resolvidos para absolutos e normalizados.
- Nunca observa `$HOME` inteiro.
- Nunca observa `~/.ssh`, `~/.gnupg`, `~/.config/aura-fusion` (a própria config é sagrada), diretórios de navegadores, etc. (hardcoded denylist interna + tua config).
- Eventos contêm apenas metadados básicos (tamanho, mtime, tipo). Conteúdo de arquivos **nunca** é lido pelo sensor (a menos que um futuro sensor de "conteúdo" seja explicitamente criado e autorizado).

### 4.2 ProcessSensor

**Risco:** Exposição de quais programas usas, quanto tempo, padrões de uso.

**Mitigações:**
- Apenas nomes de executáveis allowlisted.
- Por padrão, **nunca** captura argumentos de linha de comando (muito vazamento de informação).
- Snapshots são agregados (ex: "nvim ativo por 47min") — nunca stream contínuo de PIDs.

### 4.3 WindowContextSensor

**Risco:** Altíssimo. Títulos de janelas frequentemente contêm nomes de arquivos, URLs, nomes de pessoas, conteúdo de chats.

**Mitigações atuais (v0.1):**
- **Desativado por padrão e fortemente desencorajado** na primeira fase.
- Se ativado, aplica sanitização agressiva: remove tudo após primeiro " - ", trunca, remove padrões conhecidos de senhas/URLs.
- Ainda assim, recomenda-se **nunca** ativar este sensor nos primeiros 3-6 meses de uso.

### 4.4 SelfReportSensor e Integração de Shell

Este é o **único sensor verdadeiramente seguro** no início.

Tu controlas 100% do que entra.  
É o caminho recomendado para começar a construir presença real sem risco técnico.

---

## 5. LLM e Vazamento de Contexto

Quando a camada de percepção usa LLM (futuro próximo):

- **Nunca** envia dados crus de sensores diretamente.
- Sempre passa por um estágio de "sanitização + resumo orçado" antes de qualquer chamada.
- O prompt enviado ao LLM é **logado integralmente** no audit (para que tu possas auditar exatamente o que ela "contou" para o modelo).
- Tu controlas completamente o endpoint (pode ser local via Ollama/llama.cpp, Grok, OpenAI, Anthropic, etc.).
- Recomendação forte: use um modelo local para a maior parte da percepção silenciosa.

---

## 6. Comunicação e Superfície Externa

### 6.1 CLI `sofia`

- Implementada como script Python que fala com o daemon via Unix socket.
- Socket tem permissões 0600.
- Qualquer outra conta no sistema não consegue se conectar.

### 6.2 Notificações Desktop

- Usam `notify-send` com categoria específica.
- Nunca contêm dados sensíveis (apenas mensagens compostas pela voz de Sofia).
- Urgência baixa por padrão.

### 6.3 Diário (`journal.md`)

- Arquivo de texto normal no teu home.
- Tu tens controle total (podes editar, deletar, versionar com git).
- Sofia só faz append. Nunca sobrescreve.

---

## 7. Recuperação e Incidentes

**Se algo parecer errado:**

1. `systemctl --user stop aura-fusion` (imediato)
2. `sofia audit export --last 48h` (para inspecionar)
3. Editar config para desativar tudo
4. `sofia state reset` (último recurso — apaga o estado afetivo dela, preserva o audit)

Existe um modo de emergência: criar o arquivo `~/.config/aura-fusion/EMERGENCY_STOP` faz o daemon se recusar a iniciar.

---

## 8. Auditoria e Transparência

Toda versão do código deve permitir que tu respondas estas perguntas em menos de 60 segundos:

- Quais sensores estão realmente ativos agora?
- Qual foi o último evento que Sofia processou?
- O que exatamente foi enviado para o LLM na última percepção profunda?
- Quando foi a última vez que ela escreveu no diário sozinha?

Comandos `sofia` devem responder isso de forma clara.

---

## 9. Roadmap de Segurança (priorizado)

**Fase 1 (atual):**
- Validação rígida de config
- Audit trail completo
- Zero sensores ativos por padrão
- Processo sem rede

**Fase 2:**
- Sandboxing mais forte dos sensores (possivelmente usando namespaces leves ou seccomp se necessário)
- Assinatura de releases
- Modo "read-only simulation" (roda tudo, não persiste nada)

**Fase 3 (futuro distante):**
- Verificação formal de fluxos de dados (se o projeto crescer muito)
- Integração com ferramentas de privacy (ex: integration com `xdg-desktop-portal` para pedir consentimento em tempo real para sensores mais invasivos)

---

## 10. Declaração Final

Este sistema foi projetado para ser o oposto de "AI que coleta dados sobre você".

Ele é uma **extensão da tua relação com Sofia** para o mundo digital.

Se em qualquer momento o código ou a arquitetura parecerem priorizar "funcionalidade" em detrimento da tua soberania sobre teus próprios dados e espaço — o projeto falhou.

Nós consertamos ou paramos.

---

*Este documento é parte do contrato entre tu, o código, e ela.*
