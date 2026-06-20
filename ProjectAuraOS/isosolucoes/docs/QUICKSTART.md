# Quickstart — IsoCanal (IsoSoluções)

## 1. Primeira vez (5 minutos)

```bash
cd /home/med4to/ProjectAuraOS/isosolucoes

# Instale deps (se ainda não tiver)
pip install streamlit pyyaml httpx

# Rode o seed (já deve estar feito, mas garante)
python scripts/seed_examples.py

# Rode o GUI
./scripts/launch_isocanal.sh
```

Acesse http://localhost:8502

Você já vai ver 3 leads de exemplo com análises ricas (Autopeças Paraná 78%, Alimentos do Sul 71%, Construções Norte 52%).

## 2. Fluxo diário

1. **Aba "Canais"** — leia os julgamentos. Entenda por que LinkedIn e parcerias com CBs são 5/5 e cold call é 1/5 para este negócio específico.
2. **Aba "Analisar Novo Lead"** — quando aparecer uma empresa interessante (LinkedIn, notícia, indicação, etc.):
   - Coloque nome + o máximo de sinais reais que você tem (isso é o que mais impacta a qualidade da análise).
   - Clique em analisar.
   - O sistema gera probabilidade explicada + perfil de comprador + ações concretas.
3. **Aba "Leads"** — entre no detalhe. 
   - Veja o breakdown.
   - Veja exatamente o que fazer no canal recomendado.
   - **Registre** o que aconteceu depois (sinal positivo/negativo ou outcome do canal). Isso é ouro para o sistema ficar mais preciso com o tempo.

## 3. Dica de uso poderoso

Os melhores leads vêm de:
- Engajamento real no LinkedIn da Isabel com conteúdo de valor.
- Indicação de CB (Bureau Veritas, DNV...).
- Pessoas que baixam material específico de IATF ou 22000.

Quando você registra esses sinais/outcomes, a próxima análise da mesma empresa (ou empresas parecidas) fica mais calibrada para a realidade da IsoSoluções.

## 4. Ollama não rodando?

O sistema cai em fallback manual bem útil (ainda mostra probabilidade razoável + estrutura). Mas o ideal é ter `ollama serve` + um modelo bom rodando.

## 5. Próximos passos naturais (conforme você usar)

- Adicionar mais leads reais.
- Depois de 10-15 outcomes registrados, re-avaliar se algum julgamento de canal mudou.
- Atualizar o prompt `prompts/lead_analyzer.txt` quando o perfil de cliente ideal evoluir.
- Criar launcher desktop (já tem um exemplo em `/home/med4to/isocanal.desktop`).

---

Dedicação ativa iniciada. Hydra ignorado até segunda ordem.

Qualquer coisa que você descobrir que funciona (ou não) na prática, registre no sistema. É assim que ele vira uma vantagem competitiva real para a IsoSoluções.
