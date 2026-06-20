#!/usr/bin/env python3
"""
Update the 'Distribuidora de Isopor' lead with the new characteristic:
"ainda não ter uma identidade digital bem consolidada"
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import get_company, save_analysis, init_db

init_db()

cid = 4

# New enriched analysis incorporating low digital identity
updated = {
    "probability": 62,
    "probability_breakdown": {
        "pressao_clientes_alimenticios_e_B2B": +22,
        "ISO9001_cada_vez_mais_exigido_por_clientes_grandes": +18,
        "rastreabilidade_e_controle_de_fornecedores": +12,
        "baixa_maturidade_digital_dificulta_abordagem_online": -10,
        "decisao_centralizada_no_dono_tradicional": -7,
        "porte_medio_distribuidora_nao_fabrica": -6,
        "potencial_14001_por_sustentabilidade_EPS": +6,
        "pode_usar_ISO_como_base_para_construir_credibilidade": +7
    },
    "identity_summary": "Distribuidora tradicional de médio porte de isopor/EPS (embalagens térmicas e isolamento). Atende indústrias de alimentos, supermercados, transportadoras e construção no Sul. Tem pouca ou nenhuma identidade digital consolidada (site básico ou inexistente, presença online fraca, sem conteúdo profissional). Opera de forma muito relacional e tradicional. Sofre pressão crescente de clientes certificados por qualidade e rastreabilidade.",
    "buyer_characteristics": {
        "likely_decision_maker_roles": [
            "Dono / Diretor (principal decisor, muitas vezes familiar)",
            "Gerente de Operações ou Comercial",
            "Responsável por Qualidade/Compras (quando existe)"
        ],
        "typical_decision_process": "Decisão fortemente centralizada no dono. Ele é tradicional, confia mais em relações pessoais, indicações e resultados práticos do que em marketing digital ou propostas sofisticadas. Libera orçamento quando sente risco real de perder cliente grande ou quando um cliente importante dá um ultimato claro. Prefere soluções simples que não exijam muita mudança cultural interna.",
        "key_pains": [
            "Clientes grandes (especialmente alimentícios e exportadores) cobrando rastreabilidade, qualidade e profissionalismo",
            "Dificuldade de controlar lotes e fornecedores de EPS de forma sistemática",
            "Reclamações recorrentes de clientes sobre qualidade ou inconsistência",
            "Auditorias de segunda parte cada vez mais exigentes",
            "Falta de processos documentados que deem credibilidade",
            "Identidade digital fraca — difícil ser encontrado ou parecer profissional para clientes novos"
        ],
        "what_they_value": [
            "Abordagem prática e sem burocracia excessiva",
            "Resultados rápidos que protejam os contratos existentes",
            "Alguém que entenda a realidade de distribuidora (não só de fábrica)",
            "Custo-benefício claro e ROI visível (manter ou ganhar clientes)",
            "Confiança e relação pessoal (indicação ou conversa direta)"
        ],
        "what_rejects": [
            "Abordagens digitais frias ou genéricas (LinkedIn spam, e-mail marketing)",
            "Sistemas muito pesados ou teóricos para o tamanho da operação",
            "Propostas que parecem focar em 'imagem' em vez de resolver dores reais de cliente",
            "Qualquer coisa que pareça propaganda ou 'modinha'"
        ],
        "budget_cycle_notes": "Libera quando há pressão concreta de cliente (perda de contrato ou ultimato). O dono é conservador com gastos e precisa ver ligação direta com manutenção de receita."
    },
    "recommended_channels": [
        {
            "channel_id": "cb_partnerships",
            "why_this_channel": "O canal de maior qualidade para empresas tradicionais com baixa presença digital. Muitos clientes finais já trabalham com CBs e podem indicar quando cobram ISO do distribuidor.",
            "suggested_first_action": "Fale diretamente com auditores e comerciais de Bureau Veritas, DNV ou TÜV que atendem indústrias de alimentos e embalagens no Sul. Pergunte se têm distribuidores de isopor/embalagens que estão sendo cobrados pelos clientes a terem sistema de gestão.",
            "expected_quality": "Alta"
        },
        {
            "channel_id": "events",
            "why_this_channel": "Empresas tradicionais ainda valorizam presença física e networking pessoal. Eventos de alimentos, logística, construção e embalagem são bons pontos de encontro.",
            "suggested_first_action": "Participe (ou melhor, palestre) em eventos regionais de alimentos, embalagens ou qualidade. Aborde donos de distribuidoras de forma consultiva após palestras sobre rastreabilidade ou qualidade em cadeia de suprimentos.",
            "expected_quality": "Média-Alta"
        },
        {
            "channel_id": "linkedin",
            "why_this_channel": "Ainda útil, mas com qualidade reduzida porque a empresa-alvo tem identidade digital fraca. Serve mais para pesquisa e abordagem indireta do que para conteúdo orgânico direto.",
            "suggested_first_action": "Use LinkedIn para mapear o dono e gerentes. Depois de um sinal quente (ex: indicação ou evento), envie mensagem personalizada curta: 'Vi que vocês atendem [cliente X]. Preparei um material rápido sobre os pontos de rastreabilidade que esse tipo de cliente mais cobra em distribuidores de embalagens. Posso compartilhar?'",
            "expected_quality": "Média (mais para pesquisa + follow-up quente)"
        },
        {
            "channel_id": "content_lead_magnets",
            "why_this_channel": "Qualidade mais baixa devido à maturidade digital baixa da empresa. Eles consomem pouco conteúdo online.",
            "suggested_first_action": "Ainda vale criar o material (checklist de rastreabilidade para distribuidores), mas entregue de forma mais offline ou via indicação/WhatsApp após contato inicial, não como isca digital fria.",
            "expected_quality": "Baixa-Média"
        }
    ],
    "suggested_next_action": "Priorize construir relação via auditores de CB ou networking em eventos presenciais. Evite qualquer abordagem digital fria. Quando tiver um ponto de entrada quente, ofereça material prático e curto sobre rastreabilidade para distribuidores de embalagens.",
    "model_used": "manual-enriched-for-low-digital-identity",
    "confidence_in_analysis": "Alta (ajustado especificamente para distribuidoras tradicionais com presença digital fraca)",
    "red_flags": [
        "Se o dono for muito avesso a qualquer formalização de processos, pode resistir bastante",
        "Baixa maturidade digital também significa que eles podem subestimar o valor de ter processos profissionais documentados",
        "Canal digital puro tende a falhar — precisa de abordagem mais relacional/tradicional"
    ]
}

save_analysis(cid, updated)

print("✅ Análise atualizada com sucesso para a Distribuidora de Isopor")
print("   Característica adicionada: baixa identidade digital consolidada")
print(f"   Nova probabilidade: {updated['probability']}%")
print("   Canais prioritários:", [c["channel_id"] for c in updated["recommended_channels"]])
print("\nLead atualizado no IsoCanal (company_id=4). Rode o GUI para ver no sistema.")
