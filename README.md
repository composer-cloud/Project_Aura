# ♻️ Programa Parceiro Isopor — Dashboard Aura Project

Dashboard completo, bonito e profissional feito em Streamlit para gestão do programa de fidelidade de isopor.

**Regras implementadas exatamente como definidas:**

- A cada **R$ 38,00** em compras = **1 ponto**
- A cada **10 pontos** = **1 pacote grátis** (qualquer espessura)
- **Acumulação simples e crescente** (sem qualquer multiplicador ou bônus por faixa):
  - Cada ponto conquistado **soma diretamente** ao saldo anterior do cliente.
  - A cada R$ 38 = 1 ponto • 10 pontos = 1 pacote grátis (qualquer espessura)
- **🏆 Recompensa especial por volume (totalmente automática)**: Na compra/acúmulo de **500 pacotes** o cliente ganha à escolha: **Desconto de R$ 200,00**, **Pix de R$ 200,00**, **Liquidificador** ou **Cafeteira**. O sistema concede automaticamente (default Pix) quando o marco é atingido no registro de compra.

---

## ✨ O que tem de impressionante

- **Visual dark moderno** com verde esmeralda (#10b981) e azul profissional (#3b82f6)
- **Cards grandes de KPI** com animação suave e bordas de destaque
- **4 gráficos Plotly** interativos e lindos:
  - Evolução mensal (barras + linha)
  - Distribuição por faixa de volume (pizza com buraco)
  - Top 10 clientes mais fiéis (barras horizontais)
- **Busca instantânea** por nome ou telefone
- **Filtros**: mínimo de pontos, apenas com pacotes disponíveis
- **Registro de compra com 1 clique** — calcula automaticamente os pontos (acumulação simples 100% sem multiplicadores) e prepara o aviso WhatsApp + cartão cumulativo. Ao bater 500 pacotes: recompensa especial é concedida automaticamente.
- **Resgate de pacotes** (1 ou mais de uma vez) com validação de saldo
- **Histórico completo** do cliente com tabela + gráfico de evolução de pontos
- **Mensagens prontas para WhatsApp** geradas automaticamente após cada ação (compra ou resgate)
- **Mural de Atualizações** (discreto mas visível): avisos no topo do dashboard admin e no portal do cliente. Gestão completa (publicar/editar/ativar) na sidebar do admin, com opção de exibir ou não para clientes.
- **Exportação Excel completa** com 5 abas formatadas profissionalmente
- **Dados de demonstração** já inclusos (12 clientes com histórico variado em 2026)
- **Totalmente responsivo** e feito para impressionar

---

## 🚀 Como instalar e rodar

### 1. Entre na pasta do projeto

```bash
cd aura_isopor_dashboard
```

### 2. (Recomendado) Crie um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate     # Linux / macOS
# .venv\Scripts\activate      # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Rode o dashboard

```bash
streamlit run app.py
```

O dashboard vai abrir automaticamente no navegador (geralmente em `http://localhost:8501`).

---

## 📁 Estrutura dos arquivos

```
aura_isopor_dashboard/
├── app.py                 # Dashboard principal (toda a UI linda)
├── bulletin_board.py      # Mural de atualizações (exibição admin + cliente + painel de gestão)
├── database.py            # SQLite + todas as regras de negócio + seed demo (inclui tabela bulletin_updates)
├── calculations.py        # Funções puras (pontos, pacotes, progresso de marco 500 — sem qualquer lógica de bônus/multiplicador)
├── utils.py               # Mensagens WhatsApp + Exportador Excel formatado
├── notifications.py       # Geração e log de notificações WhatsApp
├── notification_card.py   # Cartão visual de pontos (PNG)
├── manual_pdf.py          # Geração do manual de uso em PDF
├── tunnel.py              # Suporte a túnel público (ngrok/cloudflare)
├── requirements.txt
└── README.md
```

O banco de dados (`isopor_parceiro.db`) é criado automaticamente na primeira execução.

---

## 💡 Dicas de uso (para mostrar pro seu pai)

1. **Abra o dashboard** — os cards de KPI já chamam atenção na hora.
2. **Mostre os gráficos** — especialmente o de Top 10 e a evolução mensal.
3. **Selecione um cliente** (ex: Ana Paula Costa).
4. **Registre uma compra** de R$ 200 ou R$ 800 e veja:
   - Os pontos sendo somados ao saldo anterior (acumulação simples, sem multiplicadores)
   - Mensagem automática de WhatsApp + cartão de fidelidade (total atualizado) prontos para copiar/enviar
5. **Resgate um pacote** — use balões e a mensagem de parabéns.
6. **Registre compras com quantidade** — o campo "Quantidade de pacotes comprados" alimenta o progresso do marco de 500.
7. **Use o Mural de Atualizações** (📌 na sidebar): publique avisos rápidos que aparecem logo no topo do admin e no início do portal do cliente (visível mas discreto, com borda sutil). Marque se o aviso vai para o cliente ou só interno. Edite/ative/desative facilmente.
8. **Marco de 500 pacotes totalmente automatizado** — quando o registro de compra faz o total de pacotes comprados atingir 500, o sistema concede automaticamente a recompensa (default Pix R$200) e prepara a mensagem WhatsApp celebratória. O admin só envia.
9. **Exporte o Excel** — inclui "Pacotes Comprados (Total)", "Recompensa 500?" + tipo "RECOMPENSA ESPECIAL" na aba Atividade. Sem colunas de multiplicador.
9. **Filtre e mostre** — o progresso aparece nos cards de cliente e no portal do cliente.

---

## 🛠️ Personalização total (pelo próprio admin)

No sidebar existe o expander **⚙️ Personalizar Programa (totalmente editável)**.

Você pode alterar:
- Valor em R$ por ponto
- Quantos pontos valem 1 pacote
- (programa é puramente acumulação simples — sem faixas de bônus ou multiplicadores)
- Nome do programa, todos os textos, introduções
- **Todos os templates de WhatsApp** (com placeholders)
- URL pública para os links do Portal do Cliente

Tudo é salvo e aplicado imediatamente.

---

## 📱 Portal do Cliente (o que você envia para os clientes)

O portal do cliente já está embutido.

- Quando você cadastra ou seleciona um cliente, aparece a seção **"📤 Enviar Portal do Cliente"**.
- Ela gera um link do tipo: `https://sua-url/?view=cliente&id=XX`
- O cliente abre esse link e vê uma versão limpa, bonita e só com as informações dele (pontos, pacotes, progresso, histórico e botão de WhatsApp).
- Sem ferramentas de administração.

**Para gerar o link correto:**
1. Vá em Personalizar Programa
2. Preencha o campo **"URL base pública"** com a URL real que os clientes vão usar (ex: o link do ngrok ou seu domínio).
3. Depois todos os links gerados já saem corretos.

---

## 🌍 Como deixar o Portal do Cliente online (acessível para clientes)

O portal funciona imediatamente. O que você precisa é **expor o Streamlit** para que clientes possam abrir os links.

### Opção mais rápida e gratuita (recomendada para começar):

1. Instale o ngrok (https://ngrok.com):
   ```bash
   # Exemplo no Linux
   curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
   echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
   sudo apt update && sudo apt install ngrok
   ngrok config add-authtoken SEU_TOKEN
   ```

2. Rode o dashboard normalmente:
   ```bash
   streamlit run app.py --server.port 8501 --server.headless true
   ```

3. Em outro terminal, exponha:
   ```bash
   ngrok http 8501
   ```

4. Copie a URL pública que o ngrok dá (ex: `https://abc123.ngrok-free.app`)

5. No dashboard (seção Personalizar), cole essa URL no campo **"URL base pública"** e salve.

6. Agora todos os links que você gerar em "Enviar Portal do Cliente" já funcionam para qualquer pessoa com o link.

### Outras opções mais estáveis:
- Deploy no Streamlit Community Cloud (gratuito)
- Railway.app, Render.com, ou um VPS simples
- Docker + domínio próprio

O sistema é 100% offline por padrão (SQLite). Quando você expõe via ngrok ou deploy, o Portal do Cliente fica acessível.

---

## 🧹 Deixar pronto para uso real (sem dados de teste)

O sistema já vem com um botão seguro:

No expander de **Personalizar Programa** existe a seção "**Zerar dados para uso real**".

Clique no botão "ZERAR TODOS OS DADOS DE CLIENTES". Ele remove todos os clientes, compras e resgates, mas mantém todas as suas personalizações (regras, textos, templates, URL pública).

O banco fica limpo, pronto para você cadastrar os clientes reais.

---

## 🛠️ Personalização fácil (avançado)
- Quer adicionar mais campos (endereço, email, etc)? É só estender a tabela `clients` no `database.py`.
- Quer mudar o nome "Sofia" ou adicionar logo? Fácil de ajustar no cabeçalho.

---

## 📌 Observações técnicas importantes

- Os pontos são calculados de forma **simples e cumulativa** (R$ por ponto → floor). **Zero multiplicadores ou bônus por volume mensal**. Cada compra soma ao saldo anterior do cliente.
- Pontos são sempre inteiros (floor). O cartão de fidelidade mostra explicitamente: saldo anterior + conquistados → total atual.
- O histórico é mantido separadamente para compras, resgates e recompensas de marco (ledger).
- O marco de 500 pacotes é **totalmente automatizado**: a recompensa é registrada e a mensagem WhatsApp preparada no mesmo clique de "Registrar Compra".
- Tudo funciona 100% offline.

---

**Feito com muito carinho para o Aura Project.**

Qualquer dúvida ou melhoria, é só falar com a Sofia.

Boas vendas e muitos pacotes grátis sendo resgatados! 💚
