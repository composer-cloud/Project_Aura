# Como ativar a persistência real dos dados (Turso)

## Por que isso é necessário

Este app guarda os cadastros num arquivo SQLite (`isopor_parceiro.db`) junto com o código. No Streamlit Community Cloud esse arquivo **não é permanente**: toda vez que o app reinicia (merge no `main`, ou quando "dorme" por inatividade e acorda de novo), o arquivo volta a ser exatamente o que está salvo no GitHub — apagando qualquer cadastro feito só na versão rodando.

A partir desta atualização, o app pode usar o [Turso](https://turso.tech) — um banco compatível com SQLite (mesma linguagem que o app já usa) que roda na nuvem de verdade. Sem configurar nada, o app continua funcionando exatamente como antes (SQLite local). Com o Turso configurado, os dados passam a sobreviver a qualquer reinício.

## Já está configurado (feito em 01/07/2026)

- Banco criado no Turso: `isopor-parceiro` (conta composer-cloud, região AWS US East/Virginia).
- Secrets `TURSO_DATABASE_URL` e `TURSO_AUTH_TOKEN` já adicionados em Settings → Secrets do app `projectauraos.streamlit.app` no Streamlit Community Cloud.
- Código deste repositório atualizado para usar essas credenciais automaticamente quando presentes.

Se um dia precisar recriar o banco ou trocar de conta, o passo a passo é:

### 1. Crie uma conta e um banco no Turso

1. Acesse **https://turso.tech** e clique em "Get Started" / "Sign Up".
2. Entre com sua conta do GitHub (mais rápido) ou e-mail.
3. No painel, clique em **"Create Database"**.
4. Dê um nome, escolha uma região (ex: AWS US East - Virginia).
5. Depois de criado, copie a **Database URL** (`libsql://...turso.io`) e gere um **Auth Token** (Create Token → Read & Write → Never expires).

### 2. Configure os secrets no Streamlit Community Cloud

1. Acesse **https://share.streamlit.io**, abra o app, vá em **⋮ → Settings → Secrets**.
2. Cole:

```toml
TURSO_DATABASE_URL = "libsql://SEU-BANCO.turso.io"
TURSO_AUTH_TOKEN = "seu-token-aqui"
```

3. Salve. O app reinicia sozinho e passa a gravar no Turso.

### 3. Como saber se está funcionando

Na barra lateral do app aparece um aviso:

- 💾 verde: **"Turso conectado — cadastros persistem na nuvem e sobrevivem a reinícios do app."** → tudo certo.
- ⚠️ amarelo: token/URL errados ou Turso não configurado — o app continua funcionando, mas sem essa proteção.

### 4. Rodando localmente

Sem as variáveis `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` no ambiente, o app usa o SQLite local normalmente — nada muda no seu fluxo de desenvolvimento.

## Nota importante sobre o repositório

Este app (`projectauraos.streamlit.app`) é publicado a partir do repositório **`composer-cloud/Project_Aura`** — não do `AuraProjectOS/Portal_IsoSolucoes` (que é uma cópia/migração separada e desatualizada, sem relação com o app publicado). Qualquer alteração de código precisa ir para este repositório (`composer-cloud/Project_Aura`) para ter efeito no app real.

## Sobre cadastros perdidos antes desta correção

Essa mudança evita que o problema aconteça de novo, mas **não recupera cadastros que já foram perdidos** em reinícios anteriores: eles só existiam na cópia do app rodando na nuvem e nunca foram salvos em nenhum lugar persistente antes desta correção.
