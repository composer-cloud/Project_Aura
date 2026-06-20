"""
IsoCanal — Inteligência de Canais e Leads para IsoSoluções
GUI principal (Streamlit).

Foco:
- Probabilidade de o cliente começar a comprar
- Perfil rico de identidade da empresa + características reais de comprador
- Canais julgados por qualidade/funcionalidade + ações concretas value-first
- Totalmente local (Ollama) + gasto mínimo

Run with:
    cd /home/med4to/ProjectAuraOS/isosolucoes
    streamlit run app/streamlit_app.py --server.port 8502
"""

import streamlit as st
import json
import yaml
from pathlib import Path
import sys

# Make core importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import (
    init_db, create_company, list_companies, get_company, update_company,
    save_analysis, get_latest_analysis, add_signal, list_signals,
    record_channel_outcome, get_company_channel_history
)
from core.analyzer import analyze_lead, is_ollama_available

# Paths
ROOT = Path(__file__).parent.parent
CHANNELS_YAML = ROOT / "channels" / "canais.yaml"
PERFIL_MD = ROOT / "docs" / "PERFIL_EMPRESA.md"
IDEAL_MD = ROOT / "docs" / "IDEAL_CLIENT.md"

st.set_page_config(
    page_title="IsoCanal — IsoSoluções",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load channels knowledge
@st.cache_data
def load_channels():
    with open(CHANNELS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["channels"]

CHANNELS = load_channels()
CHANNEL_MAP = {c["id"]: c for c in CHANNELS}

# --- Sidebar: Company Context (permanent) ---
with st.sidebar:
    st.title("IsoCanal")
    st.caption("Inteligência de Canais + Leads | IsoSoluções")
    st.markdown("---")

    st.subheader("Contexto Fundamental")
    with st.expander("Ver Perfil da Empresa", expanded=False):
        st.markdown(PERFIL_MD.read_text(encoding="utf-8")[:2800] + "\n\n_(veja o arquivo completo em docs/)_")

    with st.expander("Cliente Ideal (critérios)", expanded=False):
        st.markdown(IDEAL_MD.read_text(encoding="utf-8")[:2200])

    st.markdown("---")
    st.caption("Foco exclusivo: identificação + auto-promoção **value-first** (sem propaganda incômoda).")
    st.caption("Ignorar Hydra e outros até segunda ordem.")

    # Live status of local brain
    if is_ollama_available():
        st.caption("🟢 Análise local (Ollama) disponível")
    else:
        st.caption("🟠 Análise local offline (usando fallback)")

# --- Main Header ---
st.header("IsoCanal — Canais de Identificação e Auto-Promoção Inteligente")
st.markdown("**IsoSoluções** — Consultoria em Sistemas de Gestão e Certificações ISO (IATF, 9001, 14001, 45001, 22000, PBQP-H)")

tab_dashboard, tab_canais, tab_leads, tab_analisar = st.tabs([
    "📊 Dashboard",
    "📡 Canais (Julgamento de Qualidade)",
    "🏢 Leads / Empresas",
    "🔍 Analisar Novo Lead (IA Local)"
])

# ============================================================
# TAB: CANAIS
# ============================================================
with tab_canais:
    st.subheader("Julgamento de Qualidade e Funcionalidade dos Canais")
    st.caption("Cada canal foi avaliado especificamente para o modelo de venda da IsoSoluções (alto toque, alta confiança, ticket médio-alto, ciclo consultivo).")

    for ch in CHANNELS:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {ch['name']}")
                st.markdown(f"**Qualidade funcional para IsoSoluções:** `{ch['quality_score']}/5`")
                st.markdown(f"**Categoria:** {ch.get('category','')} | Velocidade: {ch.get('speed','')} | Custo: {ch.get('cost','')}")
                st.markdown(f"**Melhor para:** {ch.get('best_for','')}")
                st.markdown(f"**Por que é funcional:** {ch.get('why_functional','')}")
            with col2:
                score = ch['quality_score']
                color = "🟢" if score >= 4.5 else "🟡" if score >= 3.5 else "🟠" if score >= 2.5 else "🔴"
                st.markdown(f"## {color} {score}/5")

            with st.expander("Como usar para IDENTIFICAÇÃO (encontrar quem tem potencial real)"):
                for m in ch.get("identification_methods", []):
                    st.markdown(f"- {m}")

            with st.expander("Como usar para AUTO-PROMOÇÃO (ser encontrado/respeitado sem ser chato)"):
                for t in ch.get("promotion_tactics", []):
                    st.markdown(f"- {t}")

            if ch.get("example_success"):
                st.success(f"**Exemplo que funciona:** {ch['example_success']}")
            if ch.get("anti_pattern"):
                st.error(f"**Anti-padrão (evitar):** {ch['anti_pattern']}")

            st.caption(f"Sinais que aumentam probabilidade neste canal: {', '.join(ch.get('signals_that_increase_probability', [])) or '—'}")

    st.info("Estes julgamentos são base inicial. Use o histórico de outcomes no GUI de leads para refinar ao longo do tempo (o que realmente converte para IsoSoluções).")

# ============================================================
# TAB: LEADS / EMPRESAS
# ============================================================
with tab_leads:
    st.subheader("Base de Leads")

    companies = list_companies()

    if not companies:
        st.warning("Nenhum lead cadastrado ainda. Vá na aba 'Analisar Novo Lead' para adicionar o primeiro.")
    else:
        # Summary metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total de empresas", len(companies))
        with col_b:
            hot = 0
            for c in companies:
                a = get_latest_analysis(c["id"])
                if a and a.get("probability", 0) >= 70:
                    hot += 1
            st.metric("Hot (≥70%)", hot)
        with col_c:
            st.metric("Com análise recente", sum(1 for c in companies if get_latest_analysis(c["id"])))

        st.divider()

        # Table
        table_data = []
        for c in companies:
            a = get_latest_analysis(c["id"])
            prob = a["probability"] if a else "—"
            table_data.append({
                "ID": c["id"],
                "Empresa": c["name"],
                "Setor": c.get("industry") or "—",
                "Local": c.get("location") or "—",
                "Probabilidade": f"{prob}%" if isinstance(prob, int) else prob,
                "Atualizado": c.get("updated_at", "")[:10],
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)

        # Detail selector
        selected_id = st.selectbox(
            "Selecione uma empresa para ver o perfil rico + canais recomendados",
            options=[c["id"] for c in companies],
            format_func=lambda i: next((c["name"] for c in companies if c["id"] == i), str(i)),
        )

        if selected_id:
            company = get_company(selected_id)
            analysis = get_latest_analysis(selected_id)
            signals = list_signals(selected_id)
            channel_hist = get_company_channel_history(selected_id)

            st.markdown(f"## {company['name']}")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Website:**", company.get("website") or "—")
                st.write("**CNPJ:**", company.get("cnpj") or "—")
                st.write("**Setor:**", company.get("industry") or "—")
                st.write("**Localização:**", company.get("location") or "—")
                st.write("**Porte:**", company.get("size_estimate") or "—")
            with c2:
                if company.get("notes"):
                    st.text_area("Notas / Sinais conhecidos", company["notes"], height=100, disabled=True)

            if analysis:
                st.divider()
                prob = analysis["probability"]
                prob_color = "green" if prob >= 70 else "orange" if prob >= 45 else "red"
                st.markdown(f"### Probabilidade de começar a comprar: **:{prob_color}[{prob}%]**")

                with st.expander("Breakdown da probabilidade (explicável)", expanded=True):
                    breakdown = analysis.get("probability_breakdown", {})
                    if isinstance(breakdown, dict):
                        for factor, delta in breakdown.items():
                            sign = "+" if delta >= 0 else ""
                            st.markdown(f"- **{factor}**: {sign}{delta}")

                st.markdown("**Resumo de identidade da empresa:**")
                st.write(analysis.get("identity_summary", "—"))

                st.markdown("**Características de atuação como comprador (informação de real valor):**")
                buyer = analysis.get("buyer_characteristics", {})
                if isinstance(buyer, dict):
                    for k, v in buyer.items():
                        if isinstance(v, list):
                            st.markdown(f"- **{k.replace('_',' ').title()}**: {', '.join(v)}")
                        else:
                            st.markdown(f"- **{k.replace('_',' ').title()}**: {v}")
                else:
                    st.write(buyer)

                st.markdown("### Canais recomendados para esta empresa (com ação concreta)")
                recs = analysis.get("recommended_channels", [])
                for rec in recs:
                    ch_id = rec.get("channel_id")
                    ch_info = CHANNEL_MAP.get(ch_id, {})
                    st.markdown(f"**{ch_info.get('name', ch_id)}** (qualidade base: {ch_info.get('quality_score','?')}/5)")
                    st.markdown(f"> {rec.get('why_this_channel','')}")
                    st.success(f"**Ação sugerida (value-first):** {rec.get('suggested_first_action','')}")
                    st.caption(f"Qualidade esperada para este perfil: {rec.get('expected_quality','')}")

                st.markdown(f"**Próxima ação mais inteligente:** {analysis.get('suggested_next_action','')}")

            # Log new signal / outcome
            st.divider()
            st.subheader("Registrar sinal ou resultado de canal (alimenta scoring futuro)")
            with st.form(f"signal_form_{selected_id}", clear_on_submit=True):
                sig_type = st.selectbox("Tipo de sinal", ["positive", "negative", "channel_result", "conversion"])
                desc = st.text_input("Descrição do sinal / observação")
                ch_choice = st.selectbox("Canal relacionado (se aplicável)", [""] + [c["id"] for c in CHANNELS], format_func=lambda x: CHANNEL_MAP.get(x, {}).get("name", x) if x else "—")
                impact = st.number_input("Impacto na probabilidade (delta)", -30, 30, 0, step=5)
                submitted = st.form_submit_button("Registrar sinal")
                if submitted and desc:
                    add_signal(selected_id, sig_type, desc, ch_choice or None, impact or None)
                    st.success("Sinal registrado. Rode uma nova análise para ver o efeito acumulado.")
                    st.rerun()

            # Quick channel outcome
            with st.form(f"channel_outcome_{selected_id}"):
                st.caption("Registre rapidamente o que aconteceu ao usar um canal com esta empresa")
                ch_out = st.selectbox("Canal usado", [c["id"] for c in CHANNELS], format_func=lambda x: CHANNEL_MAP.get(x,{}).get("name",x))
                outcome = st.selectbox("Resultado", ["no_contact", "engaged", "meeting_booked", "proposal_sent", "closed_won", "closed_lost", "not_fit"])
                notes_out = st.text_input("Notas breves")
                if st.form_submit_button("Salvar outcome do canal"):
                    record_channel_outcome(selected_id, ch_out, outcome, notes_out)
                    st.success("Outcome registrado. Isso ajuda a refinar julgamentos futuros.")
                    st.rerun()

            if signals:
                with st.expander(f"Histórico de sinais ({len(signals)})"):
                    for s in signals:
                        st.markdown(f"- [{s['created_at'][:10]}] **{s['signal_type']}** ({s.get('channel_id') or ''}): {s['description']} {'(impacto ' + str(s['impact_on_probability']) + ')' if s.get('impact_on_probability') else ''}")

# ============================================================
# TAB: ANALISAR NOVO LEAD
# ============================================================
with tab_analisar:
    st.subheader("Analisar Empresa com IA Local (Ollama)")

    ollama_ok = is_ollama_available()
    if ollama_ok:
        st.success("Ollama local detectado — análise com modelo especializado ativa.")
    else:
        st.warning("Ollama não está respondendo agora. Vai usar fallback (ainda gera estrutura boa + probabilidade razoável, mas menos precisa). Rode `ollama serve` + seu modelo preferido para máxima qualidade.")

    st.caption("Preencha o que você sabe. O modelo local especializado em IsoSoluções vai gerar probabilidade explicável + perfil de comprador + recomendações de canais com ações concretas.")

    with st.form("new_lead_form"):
        name = st.text_input("Nome da empresa *", placeholder="Ex: Metalúrgica XYZ Fornecedora Ltda")
        col1, col2 = st.columns(2)
        with col1:
            website = st.text_input("Website", placeholder="https://...")
            industry = st.text_input("Setor / Indústria", placeholder="Fornecedor automotivo tier 2 / Autopeças / Alimentos processados...")
            location = st.text_input("Localização", placeholder="São José dos Pinhais, PR")
        with col2:
            size = st.text_input("Porte estimado", placeholder="70-120 funcionários / Médio porte industrial")
        notes = st.text_area(
            "Sinais / Notas conhecidas (o mais importante para boa análise)",
            height=120,
            placeholder="Ex: Acabou de ganhar fornecimento para montadora e precisa de IATF em 7 meses. Gerente de Qualidade postou no LinkedIn sobre dificuldade com auditoria de PPAP e Core Tools. Empresa familiar em expansão."
        )
        model = st.text_input("Modelo Ollama (deixe default se não souber)", value="qwen2.5:7b")

        submitted = st.form_submit_button("🔍 Analisar com IA Local + Salvar Lead", type="primary")

    if submitted:
        if not name.strip():
            st.error("Nome da empresa é obrigatório.")
        else:
            with st.spinner("Analisando com modelo local (pode demorar 30-90s dependendo do modelo)..."):
                result = analyze_lead(
                    name=name.strip(),
                    website=website.strip() or None,
                    industry=industry.strip() or None,
                    location=location.strip() or None,
                    size_estimate=size.strip() or None,
                    notes=notes.strip() or None,
                    model=model.strip(),
                )

            # Save company + analysis
            company_id = create_company(
                name=name.strip(),
                website=website.strip() or None,
                industry=industry.strip() or None,
                location=location.strip() or None,
                size_estimate=size.strip() or None,
                notes=notes.strip() or None,
            )
            save_analysis(company_id, result)

            st.success(f"Lead salvo (ID {company_id}). Análise gerada.")

            # Show result immediately
            st.divider()
            prob = result["probability"]
            st.markdown(f"## Probabilidade estimada: **{prob}%**")

            st.markdown("### Breakdown (fatores que mais pesaram)")
            for factor, delta in result.get("probability_breakdown", {}).items():
                sign = "+" if isinstance(delta, (int, float)) and delta >= 0 else ""
                st.markdown(f"- {factor}: {sign}{delta}")

            st.markdown("### Identidade da empresa (contexto)")
            st.write(result.get("identity_summary", "—"))

            st.markdown("### Características do comprador (informação de real valia)")
            buyer = result.get("buyer_characteristics", {})
            if isinstance(buyer, dict):
                for k, v in buyer.items():
                    label = k.replace("_", " ").title()
                    if isinstance(v, list):
                        st.markdown(f"**{label}:** {', '.join(map(str, v))}")
                    else:
                        st.markdown(f"**{label}:** {v}")
            else:
                st.write(buyer)

            st.markdown("### Canais recomendados + ação concreta (value-first)")
            for rec in result.get("recommended_channels", []):
                ch = CHANNEL_MAP.get(rec.get("channel_id"), {})
                st.markdown(f"**{ch.get('name', rec.get('channel_id'))}** — Qualidade base: {ch.get('quality_score','?')}/5")
                st.info(rec.get("why_this_channel", ""))
                st.success(f"Ação sugerida: {rec.get('suggested_first_action', '')}")

            st.markdown(f"**Próxima ação recomendada:** {result.get('suggested_next_action','')}")

            if result.get("red_flags"):
                for flag in result["red_flags"]:
                    st.warning(f"⚠️ {flag}")

            st.caption("Vá na aba 'Leads / Empresas' para ver o registro completo, adicionar mais sinais e registrar outcomes de canais.")

# ============================================================
# TAB: DASHBOARD (simple but useful)
# ============================================================
with tab_dashboard:
    st.subheader("Visão Geral — Onde está o esforço de canais valendo a pena?")
    companies = list_companies()

    if not companies:
        st.info("Cadastre alguns leads na aba Analisar para ver o dashboard.")
    else:
        # Quick stats
        probs = []
        for c in companies:
            a = get_latest_analysis(c["id"])
            if a:
                probs.append(a["probability"])

        if probs:
            avg = sum(probs) / len(probs)
            st.metric("Probabilidade média da carteira atual", f"{avg:.0f}%")

        st.markdown("### Top recomendações de canal (agregado das últimas análises)")
        channel_counts = {}
        for c in companies:
            a = get_latest_analysis(c["id"])
            if a:
                for rec in a.get("recommended_channels", []):
                    cid = rec.get("channel_id")
                    channel_counts[cid] = channel_counts.get(cid, 0) + 1

        if channel_counts:
            for cid, count in sorted(channel_counts.items(), key=lambda x: -x[1]):
                ch = CHANNEL_MAP.get(cid, {})
                st.markdown(f"- **{ch.get('name', cid)}** recomendado para {count} lead(s) na base atual")

        st.markdown("---")
        st.caption("Dica: quanto mais sinais e outcomes você registrar nos leads, mais preciso o sistema fica para IsoSoluções especificamente.")

# Footer
st.markdown("---")
st.caption("IsoCanal é peça de contexto fundamental da IsoSoluções. Funções específicas de identificação, scoring de probabilidade, perfil de comprador e julgamento de canais vivem aqui. Dedicação ativa iniciada em junho/2026.")
