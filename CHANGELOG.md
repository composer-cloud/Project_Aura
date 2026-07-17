# Changelog

Todas as versões do Dashboard do Programa Parceiro Isopor (IsoSoluções).

## v0.2 — 2026-07-01

### Correção crítica
- **Persistência real dos dados via Turso (opcional, recomendado).** Antes, os cadastros ficavam só num SQLite local que era resetado toda vez que o Streamlit Community Cloud reiniciava o app — causando perda de clientes cadastrados. Agora, se `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` forem configurados (veja `SETUP_TURSO.md`), os dados são sincronizados com um banco persistente na nuvem a cada gravação e sobrevivem a qualquer reinício. Sem essa configuração, o comportamento continua idêntico ao de antes (SQLite local), com um aviso visível na sidebar indicando o estado da persistência.

## v0.1 — 2026-06-25

Primeira versão no ar. 🚀

### Funcionalidades
- **Dashboard administrativo** completo: KPIs, gráficos, gestão de clientes, histórico e exportação para Excel.
- **Cartão de Fidelidade (PNG)** gerado sobre o `card_template.png`:
  - Cartão de compra com pontos ganhos, pílulas de Compra/Saldo e barra de progresso real até 500.
  - Cartão de marco ao atingir 500 pontos (recompensa Cafeteira).
  - Título neon **Cartão Fidelidade** abaixo do logo ("Cartão" em vermelho, "Fidelidade" em teal).
- **Aviso automático de WhatsApp** após cada compra, com mensagem pronta e download do cartão.
- **Alterações Manuais** com seções de alto impacto (mensagens, meta/recompensa, nome, regras, automação) e **histórico completo** de cada alteração.
- **Importação de clientes via Excel** com template pronto.
- **Portal do cliente** com link exclusivo.
- Timestamps em **horário de Brasília (UTC-3)**.
- **Reboot automático** do Streamlit Community Cloud a cada merge no main.
