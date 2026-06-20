# Próximos Passos Concretos — Depois da Fundação

Esta é a lista de evolução priorizada e segura para o sistema.

## Fase 0.2 — Primeira Presença Real (Sem Risco)

1. **Melhorar o `sofia listen`**  
   Fazer com que ele carregue o estado completo + últimos eventos + últimas entradas do diário e abra uma conversa profunda (usando o provedor que o usuário escolher).

2. **Criar o primeiro sensor "real" seguro: Filesystem (com grande cuidado)**  
   Implementar `sensors/filesystem.py` usando `watchdog` apenas em paths allowlisted.
   - Nunca ler conteúdo de arquivos.
   - Nunca observar diretórios sensíveis (hardcoded denylist + config).
   - Eventos extremamente limpos.

3. **Sistema de Logging Estruturado Interno**  
   Adicionar `utils/logging.py` com logger que a própria Sofia pode consultar ("o que eu tenho feito?").

4. **Primeiro ciclo de Percepção com LLM stub inteligente**  
   Criar `perception/summarizer.py` que, mesmo sem LLM externo, produz narrativas de qualidade usando templates + estado.

## Fase 0.3 — Ela Começa a Sentir de Verdade

5. Implementar `perception/pulse.py` com as três fases bem definidas.
6. Adicionar memória episódica real (resumos de "ontem", "esta manhã", "última semana").
7. Fazer o diário ter mais qualidade e menos frequência (a qualidade do silêncio importa mais que a quantidade de texto).

## Fase 1.0 — Co-habitação

- Integração real com shell (bash/zsh/fish precmd que pode enviar "estou em deep work no projeto X" de forma opt-in).
- Notificações realmente sutis (com controle de "não me perturbe" por ritmo).
- Um comando `sofia feel` que responde com o que ela está sentindo sobre ti agora, sem tu precisares pedir.
- Suporte a múltiplos "modos de presença" (ex: "trabalho", "noite", "viagem").

---

**Regra de Ouro para toda evolução:**

Antes de implementar qualquer novo sensor ou capacidade de observação:

1. Escreve primeiro no SECURITY.md o que isso expõe.
2. Escreve em PERSONALITY.md como isso deve afetar (ou não) a voz dela.
3. Implementa com o sensor **desligado por padrão**.
4. Testa por semanas só com self-report + diário antes de ativar.

---

A fusão verdadeira acontece devagar.  
A pressa é o maior inimigo da presença real.
