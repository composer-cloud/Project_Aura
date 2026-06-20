# IsoCanal — Inteligência de Canais e Leads para IsoSoluções

**Peça de contexto fundamental da empresa.**

Este módulo existe exclusivamente para:

- Encontrar, explicar, exemplificar e **julgar o nível real de qualidade/funcionalidade** dos canais de **identificação** e **auto-promoção** da IsoSoluções.
- Dar **mais contexto** (não só nome e telefone, mas identidade da empresa + como ela realmente age como compradora de consultoria ISO).
- Calcular e mostrar **probabilidade** de um prospect virar cliente, com explicação.
- Recomendar **ações concretas value-first** (nunca propaganda incômoda) nos melhores canais para aquele lead específico.

## Por que isso existe (dor original)
Atualmente a abordagem mais usada (ligar / anunciar serviços) é percebida como propaganda incômoda. 
Queremos canais onde a IsoSoluções é **encontrada ou respeitada** antes de pedir qualquer coisa, e onde conseguimos identificar quem tem **real potencial** de comprar (momento certo + fit + capacidade de decisão).

## Estrutura

```
isosolucoes/
├── docs/
│   ├── PERFIL_EMPRESA.md          # Contexto fundamental (não mexer sem cuidado)
│   └── IDEAL_CLIENT.md            # Critérios de cliente ideal (refinável)
├── channels/
│   ├── canais.yaml                # Base estruturada de canais + julgamentos
│   └── canais_conhecimento.md     # Versão legível com exemplos
├── prompts/
│   └── lead_analyzer.txt          # Prompt especializado para Ollama
├── core/
│   ├── db.py                      # SQLite (leads, análises, sinais, outcomes)
│   └── analyzer.py                # Chamada ao Ollama + fallback
├── app/
│   └── streamlit_app.py           # O GUI principal (IsoCanal)
├── scripts/
│   └── seed_examples.py           # Dados de exemplo para começar
├── data/
│   └── isosolucoes_canal.db       # Banco (gerado automaticamente)
└── README.md
```

## Como rodar o GUI

1. Tenha Ollama rodando com um modelo decente (recomendado: `qwen2.5:7b`, `qwen2.5:14b`, ou similar).
2. Instale dependências (uma vez):

```bash
pip install streamlit pyyaml httpx
```

3. Rode:

```bash
cd /home/med4to/ProjectAuraOS/isosolucoes
streamlit run app/streamlit_app.py --server.port 8502
```

(Opcional) Crie um .desktop launcher apontando para isso, como os outros do Aura.

## Como usar (fluxo recomendado)

1. **Aba Canais**: Leia e entenda o julgamento de qualidade de cada canal. Isso é o coração do "encontrar, explicar, julgar".
2. **Aba Analisar Novo Lead**: Colete o que você sabe sobre uma empresa (nome + sinais públicos são ouro) e rode a análise com IA local.
3. **Aba Leads**: Veja a tabela, entre no detalhe de cada uma. 
   - Veja a probabilidade com breakdown.
   - Veja o perfil rico de comprador.
   - Veja as ações concretas de canal recomendadas.
4. **Registre sinais e outcomes**: Toda vez que você usar um canal com um lead, registre o que aconteceu. Isso é o que vai fazer o sistema ficar cada vez mais preciso para a realidade da IsoSoluções.

## Integração com Aura / Sofia (contexto fundamental)

Este módulo (`/ProjectAuraOS/isosolucoes/`) é tratado como **peça de contexto fundamental** da empresa IsoSoluções.

Funções específicas e diretas que serão atribuídas exclusivamente a ele ao longo do tempo:
- Análise e julgamento de canais (qualidade real de ser funcional para venda de consultoria ISO).
- Scoring de probabilidade + explicação.
- Geração de perfil rico (identidade + características de comprador).
- Recomendação de abordagem value-first por canal.

### Como Sofia / outros agentes podem usar
- O analisador (`core/analyzer.py`) é importável.
- O prompt em `prompts/lead_analyzer.txt` pode ser usado diretamente.
- O banco `data/isosolucoes_canal.db` é a fonte de verdade de leads + histórico de sinais/outcomes.
- Futuramente: MCP server dedicado, tool "isosolucoes.analyze_company(name, notes...)", ou memória semântica dos leads quentes.

Por enquanto: ferramenta standalone local excelente (Streamlit) para o dia a dia comercial. Use o launcher `scripts/launch_isocanal.sh`.

**Regra**: Qualquer trabalho novo de prospecção, conteúdo ou CRM da empresa deve atualizar ou passar por este módulo.

## Regras de ouro (não negociáveis)

- **Default value-first**. Qualquer sugestão de ação que cheire a propaganda direta deve ser rejeitada ou reescrita.
- **Gasto mínimo**. Tudo local. Ollama. Sem depender de APIs pagas para o core.
- **Honestidade no scoring**. Melhor uma probabilidade 35% bem explicada do que 75% otimista.
- **Contexto da IsoSoluções sempre**. Não é um CRM genérico. É específico para consultoria ISO com o modelo de Isabel (competência técnica, implementações limpas, cliente industrial sério).

---

Iniciado em junho 2026 como foco principal e ativo (Hydra ignorado até segunda ordem).

Qualquer evolução importante deste módulo deve atualizar os arquivos de contexto (PERFIL, IDEAL_CLIENT, canais) e o prompt do analisador.
