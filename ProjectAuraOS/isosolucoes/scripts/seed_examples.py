"""
Seed 3-4 realistic example leads for IsoSoluções so the GUI is useful on first run.
Run once:
    python scripts/seed_examples.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import init_db, create_company, save_analysis, add_signal

init_db()

examples = [
    {
        "name": "Autopeças Paraná Ltda",
        "website": "https://www.autopecasparana.com.br",
        "industry": "Fornecedor automotivo tier 2 (injeção plástica e usinagem)",
        "location": "São José dos Pinhais, PR",
        "size_estimate": "120-180 funcionários",
        "notes": "Ganhou fornecimento para montadora europeia em 2025. Precisa de IATF 16949 em até 9 meses. Gerente de Qualidade (Carlos) postou no LinkedIn sobre dificuldade com PPAP e auditoria de processo. Já tem ISO 9001 mas o sistema é fraco para automotivo.",
        "analysis": {
            "probability": 78,
            "probability_breakdown": {
                "IATF_automotivo_tier2": +28,
                "ultimato_cliente_montadora": +22,
                "expansao_contrato_novo": +15,
                "ja_tem_9001_mas_fraco": -8,
                "porte_bom_para_consultoria": +8,
                "regiao_PR_forte_atuacao_IsoSolu": +13,
            },
            "identity_summary": "Fornecedor automotivo de médio porte em expansão no Paraná, com pressão real de cliente (montadora) para certificação IATF. Já possui base ISO 9001 mas claramente insuficiente para exigências automotivas.",
            "buyer_characteristics": {
                "likely_decision_maker_roles": ["Gerente de Qualidade", "Diretor Industrial", "Engenheiro de Qualidade Sênior"],
                "typical_decision_process": "Qualidade lidera tecnicamente, mas Diretoria Industrial e Comercial (contrato com montadora) têm poder de veto. Costumam comparar 2-3 propostas e valorizam muito 'quem já fez IATF limpa em fornecedor similar'.",
                "key_pains": ["PPAP e Core Tools fracos", "NCs em auditoria de cliente", "Sistema 9001 não escala para IATF", "Prazo apertado de 9 meses"],
                "what_they_value": ["Consultor com experiência real em IATF automotivo", "Implementação que não para a fábrica", "Suporte forte durante auditoria de certificação e de cliente"],
                "what_rejects": ["Propostas genéricas de 'ISO'", "Consultores que nunca trabalharam com montadora", "Sistemas muito burocráticos que a produção odeia"],
                "budget_cycle_notes": "Quando há contrato novo com montadora, orçamento costuma ser liberado com relativa rapidez (prioridade estratégica)."
            },
            "recommended_channels": [
                {
                    "channel_id": "linkedin",
                    "why_this_channel": "O Gerente de Qualidade (Carlos) está ativo no LinkedIn falando de problemas de PPAP. Canal perfeito para abordagem value-first sem interrupção.",
                    "suggested_first_action": "Comentar o post dele sobre PPAP com insight prático sobre uma cláusula específica da IATF que costuma ser armadilha em empresas de injeção que estão subindo de tier. Oferecer checklist de 1 página.",
                    "expected_quality": "Alta"
                },
                {
                    "channel_id": "events",
                    "why_this_channel": "Empresas automotivas de PR/SC costumam mandar gente para o Fórum IQA. Alta chance de encontrar o time de qualidade lá.",
                    "suggested_first_action": "Se for palestrar ou patrocinar o próximo Fórum IQA, preparar material específico sobre 'IATF para fornecedores de injeção plástica que estão subindo de tier'.",
                    "expected_quality": "Alta"
                }
            ],
            "suggested_next_action": "Abordagem no LinkedIn do Gerente de Qualidade com valor específico sobre PPAP/IATF antes de qualquer menção a serviços.",
            "model_used": "seed-example",
            "raw_llm_output": "Seed data for immediate usability of the GUI."
        }
    },
    {
        "name": "Alimentos do Sul S.A.",
        "website": "",
        "industry": "Indústria de alimentos processados (carnes e derivados)",
        "location": "Chapecó, SC",
        "size_estimate": "350+ funcionários, exportação para Europa e Ásia",
        "notes": "Está se preparando para certificação ISO 22000 + FSSC porque um grande cliente varejista europeu exigiu. Tiveram NCs na última auditoria de cliente relacionada a controle de alergênicos e rastreabilidade. Diretora de Qualidade (Regina) é muito técnica.",
        "analysis": {
            "probability": 71,
            "probability_breakdown": {
                "exigencia_cliente_exportacao": +25,
                "setor_alimentos_22000": +18,
                "NCs_recentes_em_auditoria_cliente": +15,
                "porte_grande_com_orcamento": +12,
                "regiao_SC_atuacao_IsoSolu": +8,
                "diretora_qualidade_tecnica": +5,
                "sem_ultimato_de_morte": -12,
            },
            "identity_summary": "Grande indústria alimentícia exportadora em SC com exigência concreta de cliente internacional para ISO 22000/FSSC. Já tem algum sistema mas com falhas visíveis em pontos críticos de segurança de alimentos.",
            "buyer_characteristics": {
                "likely_decision_maker_roles": ["Diretora de Qualidade / Segurança de Alimentos", "Gerente de Produção", "Diretor Industrial"],
                "typical_decision_process": "Muito técnico. Decisão passa por análise detalhada da metodologia de implantação, experiência do consultor com alimentos e exportação, e garantia de que não vai gerar NCs que prejudiquem a certificação junto ao cliente europeu.",
                "key_pains": ["Alergênicos e rastreabilidade", "Pressão de cliente varejista europeu", "Auditorias de segunda parte frequentes"],
                "what_they_value": ["Consultor com forte background em 22000/FSSC e auditoria de cliente", "Capacidade de treinar o time de produção (não só papel)", "Histórico de implementações limpas em alimentos"],
                "what_rejects": ["Abordagem genérica de 'qualidade'", "Consultores sem vivência em exportação/alimentos"],
                "budget_cycle_notes": "Quando há exigência de cliente grande, o orçamento costuma vir mais fácil, mas eles são exigentes na escolha."
            },
            "recommended_channels": [
                {
                    "channel_id": "linkedin",
                    "why_this_channel": "Diretora de Qualidade técnica costuma consumir e interagir com conteúdo bom sobre segurança de alimentos.",
                    "suggested_first_action": "Publicar ou comentar com conteúdo específico sobre 'alergênicos em linhas de produção de carnes processadas' ou 'rastreabilidade um passo atrás e um passo à frente na prática'.",
                    "expected_quality": "Alta"
                },
                {
                    "channel_id": "cb_partnerships",
                    "why_this_channel": "Empresas de alimentos com exportação quase sempre já conversam com Bureau Veritas ou DNV. Indicação de CB seria ouro.",
                    "suggested_first_action": "Fortalecer relação com os auditores de alimentos da BV e DNV que atuam em SC.",
                    "expected_quality": "Muito Alta"
                }
            ],
            "suggested_next_action": "Criar e compartilhar (LinkedIn ou via parceria CB) material prático sobre os pontos de NC que empresas de carnes mais sofrem em auditorias de cliente europeu.",
            "model_used": "seed-example",
        }
    },
    {
        "name": "Construções Norte Ltda",
        "website": "",
        "industry": "Construtora de médio porte (obras industriais e infraestrutura)",
        "location": "Joinville, SC",
        "size_estimate": "60-90 funcionários",
        "notes": "Está participando de licitações públicas e grandes obras privadas que estão começando a exigir PBQP-H + ISO 9001. O dono (engenheiro) é quem decide quase tudo. Sistema atual é muito informal. Não têm ninguém dedicado full-time em qualidade.",
        "analysis": {
            "probability": 52,
            "probability_breakdown": {
                "exigencia_licitacao_PBQP-H": +18,
                "setor_construcao_civil": +10,
                "porte_medio": +5,
                "sem_area_qualidade_dedicada": -15,
                "decisao_concentrada_no_dono": -8,
                "sem_ultimato_urgente": -10,
            },
            "identity_summary": "Construtora familiar de médio porte em SC que está sentindo pressão de mercado (licitações) para ter sistema de gestão formal, mas ainda não tem estrutura interna forte para isso.",
            "buyer_characteristics": {
                "likely_decision_maker_roles": ["Dono / Diretor (engenheiro)", "Gerente de Obras"],
                "typical_decision_process": "Decisão muito centralizada no dono. Ele compara preço com bastante peso e costuma querer 'o mínimo necessário para passar na licitação'.",
                "key_pains": ["Exigência em licitações", "Sistema muito informal / baseado em pessoas"],
                "what_they_value": ["Preço competitivo", "Algo que 'não atrapalhe a obra'", "Rapidez"],
                "what_rejects": ["Sistemas muito pesados e burocráticos", "Propostas caras sem prova de resultado em construtoras"],
                "budget_cycle_notes": "Só liberam quando a licitação realmente exige e o contrato está quase fechado. Ciclo de decisão rápido mas sensível a preço."
            },
            "recommended_channels": [
                {
                    "channel_id": "content_lead_magnets",
                    "why_this_channel": "Construtoras respondem bem a materiais práticos ('Checklist PBQP-H para obras industriais', 'O que muda na prática quando a licitação exige sistema').",
                    "suggested_first_action": "Criar e divulgar (LinkedIn + site) um material curto e direto sobre 'PBQP-H sem complicar a vida da obra'. Usar como isca.",
                    "expected_quality": "Média-Alta"
                }
            ],
            "suggested_next_action": "Não investir energia pesada ainda. Oferecer o material prático e ver se o dono demonstra dor real ou só curiosidade de licitação.",
            "model_used": "seed-example",
        }
    },
]

for ex in examples:
    cid = create_company(
        name=ex["name"],
        website=ex.get("website"),
        industry=ex.get("industry"),
        location=ex.get("location"),
        size_estimate=ex.get("size_estimate"),
        notes=ex.get("notes"),
    )
    save_analysis(cid, ex["analysis"])
    # Add one positive signal example
    add_signal(cid, "positive", "Lead criado via seed com sinais públicos fortes de demanda", None, +5)

print("Seed data inserted successfully.")
print(f"Created {len(examples)} example companies.")
