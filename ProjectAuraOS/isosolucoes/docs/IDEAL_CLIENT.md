# Perfil de Cliente Ideal — IsoSoluções (refinável no GUI)

## Critérios de Fit (usados para scoring inicial)

### 1. Fit de Setor / Norma (peso alto)
- **Muito alto**: Fornecedores automotivos (IATF 16949) — especialmente tier 2 que fornecem para montadoras que cobram IATF.
- Alto: Indústria de alimentos / bebidas com exportação ou clientes exigentes (ISO 22000, FSSC, BRC).
- Alto: Construção civil / engenharia com obras públicas ou grandes empreiteiras (PBQP-H + ISO 9001).
- Médio-alto: Indústria em geral buscando ISO 9001 + 14001 + 45001 integrados (redução de custo + imagem).
- Baixo: Serviços puros (contabilidade, advocacia, varejo pequeno), microempresas sem cadeia de fornecimento exigente.

### 2. Sinais de Momento / Dor (os mais fortes para probabilidade)
- Recentemente perdeu certificado ou teve auditoria com muitas NCs graves.
- Cliente importante (montadora, rede de supermercados, construtora grande) deu ultimato de certificação em X meses.
- Está expandindo planta / linha de produção / número de funcionários rápido e o sistema de gestão atual "não dá conta".
- Está contratando Gerente/Supervisor de Qualidade ou "Analista de Sistemas de Gestão" (sinal de que vão profissionalizar).
- Notícia de exportação nova, licitação ganha que exige sistema certificado, ou fusão/aquisição.
- Reclamações públicas ou posts internos de dificuldade com auditorias / "burocracia da qualidade".

### 3. Tamanho / Capacidade de Pagar
- 50-500+ colaboradores (faixa doce da maioria das implementações sérias de consultoria).
- Tem área de Qualidade/SGI com pelo menos 1 pessoa dedicada (mesmo que sobrecarregada).
- Faturamento estimado que justifica investimento de R$ 15k-60k+ em consultoria (depende da complexidade da norma).

### 4. Características de Atuação como Comprador (crítico para o GUI)
- **Decisor principal**: Geralmente Gerente/Diretor de Qualidade ou Operações. Em empresas menores/familiares: o sócio/diretor industrial.
- **Processo de decisão**: Raro ser compra impulsiva. Envolve:
  - Diagnóstico interno ou conversa com certificadora.
  - Comparação de propostas (preço x profundidade x histórico de NCs do consultor).
  - Alinhamento com a certificadora que eles já usam ou vão usar.
- Valorizam: Experiência comprovada na norma exata + setor, "não complicar a vida da fábrica", capacidade de treinar o time interno, suporte durante a auditoria de certificação.
- Rejeitam: Consultores que "só entregam papel" ou que criam sistemas engessados que a operação odeia.
- Ciclo de venda típico: 1-4 meses de conversa + diagnóstico até fechamento. Implementação 3-9 meses.

## Sinais Negativos Fortes (reduzem probabilidade drasticamente)
- "Quero o certificado o mais barato e rápido possível".
- Já têm um consultor fixo com quem estão satisfeitos.
- Micro ( < 20 pessoas) sem cliente exigindo a certificação.
- Setor de serviços de baixa regulamentação.
- Histórico de trocar de consultor a cada ciclo (sinal de que não implementam de verdade).

## Como usar no GUI
O analisador de lead deve produzir:
- Um score de probabilidade (0-100) com breakdown explicável (ex: +25 IATF automotivo, +18 ultimato de cliente, -12 microempresa sem estrutura...).
- Um resumo curto de "identidade da empresa".
- Um resumo de "como essa empresa costuma comprar consultoria de sistemas de gestão".
- 2-3 canais recomendados + uma sugestão concreta de primeiro passo value-first (ex: "Comentar no LinkedIn do Gerente de Qualidade com insight sobre IATF 16949:2016 cláusula X que mudou em 202X").

Este documento deve ser atualizado conforme o GUI acumular dados reais de leads que converteram ou não.
