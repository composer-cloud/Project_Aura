"""
IsoSoluções Canal - Local LLM Analyzer
Uses Ollama (http://localhost:11434) for zero-cost, private analysis.
Falls back gracefully if Ollama is not running.
"""

import json
import httpx
from pathlib import Path
from typing import Optional, Dict, Any

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "lead_analyzer.txt"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"   # or other Qwen-compatible model that user has

def is_ollama_available() -> bool:
    """Fast check if local Ollama is reachable and responding."""
    try:
        with httpx.Client(timeout=2.0) as client:
            r = client.get("http://localhost:11434/api/tags")
            return r.status_code == 200
    except Exception:
        return False

def load_prompt_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def analyze_lead(
    name: str,
    website: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    size_estimate: Optional[str] = None,
    notes: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    timeout: float = 45.0,
) -> Dict[str, Any]:
    """
    Calls local Ollama with the specialized IsoSoluções prompt.
    Returns structured dict (or fallback dict on error).
    """
    template = load_prompt_template()
    prompt = template.format(
        name=name or "Não informado",
        website=website or "Não informado",
        industry=industry or "Não informado",
        location=location or "Não informado",
        size_estimate=size_estimate or "Não informado",
        notes=notes or "Nenhum sinal adicional informado.",
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,   # low temp for structured, consistent output
            "num_predict": 1800,
        },
        "format": "json",   # Ollama will try to enforce JSON
    }

    try:
        # Very fast health check — if this fails, we immediately fallback (no long hangs)
        with httpx.Client(timeout=2.5) as client:
            health = client.get("http://localhost:11434/api/tags", timeout=2.0)
            if health.status_code != 200:
                raise RuntimeError("Ollama health check failed")

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("response", "").strip()

            # Aggressive JSON extraction (many models are sloppy)
            if "```" in raw:
                parts = raw.split("```")
                for p in parts:
                    p = p.strip()
                    if p.lower().startswith("json"):
                        p = p[4:].strip()
                    if p.startswith("{") and p.endswith("}"):
                        raw = p
                        break
            # Last resort: find first { ... }
            if not (raw.startswith("{") and raw.endswith("}")):
                start = raw.find("{")
                end = raw.rfind("}")
                if start != -1 and end != -1 and end > start:
                    raw = raw[start:end+1]

            parsed = json.loads(raw)

            # Basic validation + normalization
            prob = int(parsed.get("probability", 50))
            prob = max(0, min(100, prob))

            # Hybrid: if LLM gave low confidence or weird numbers, blend with rule-based
            rule_boost = simple_rule_based_probability(industry or "", notes or "")
            if prob < 30 and rule_boost > prob + 15:
                prob = min(85, (prob + rule_boost) // 2)

            recs = parsed.get("recommended_channels", [])
            if not recs:
                recs = _basic_channel_recs(industry or "", notes or "")

            result = {
                "probability": prob,
                "probability_breakdown": parsed.get("probability_breakdown", {}),
                "identity_summary": parsed.get("identity_summary", ""),
                "buyer_characteristics": parsed.get("buyer_characteristics", {}),
                "recommended_channels": recs,
                "suggested_next_action": parsed.get("suggested_next_action", ""),
                "raw_llm_output": raw,
                "model_used": model,
                "confidence_in_analysis": parsed.get("confidence_in_analysis", "Média"),
                "red_flags": parsed.get("red_flags", []),
            }
            return result

    except Exception as e:
        # Graceful fallback — still useful (now with strong hybrid rules)
        rule_p = simple_rule_based_probability(industry or "", notes or "")
        recs = _basic_channel_recs(industry or "", notes or "")
        return {
            "probability": rule_p,
            "probability_breakdown": {"rule_based_baseline": rule_p - 30, "llm_fallback": 0},
            "identity_summary": f"Empresa no setor '{industry or 'desconhecido'}'. Análise narrativa via LLM indisponível no momento — usando baseline forte de regras + seu contexto.",
            "buyer_characteristics": {
                "likely_decision_maker_roles": ["Gerente de Qualidade / SGI", "Diretor Industrial / Operações"],
                "typical_decision_process": "Envolve Quality tecnicamente + alguém com poder de liberação de orçamento (diretoria ou dono). Valorizam histórico limpo em normas específicas.",
            },
            "recommended_channels": recs,
            "suggested_next_action": "Use os canais recomendados com abordagem value-first. Registre os sinais/outcomes para refinar.",
            "raw_llm_output": str(e),
            "model_used": "hybrid-rule-fallback",
            "confidence_in_analysis": "Média (regras calibradas para IsoSoluções + LLM parcial)",
            "red_flags": [],
        }


def simple_rule_based_probability(industry: str, notes: str) -> int:
    """Stronger rule-based baseline tuned to IsoSoluções ideal client."""
    score = 30
    text = ((industry or "") + " " + (notes or "")).lower()

    # Strong positive signals for IsoSoluções
    if any(k in text for k in ["iatf", "automotiv", "tier", "montadora", "fornecedor"]):
        score += 28
    if any(k in text for k in ["ultimato", "cliente cobrou", "exigiu", "prazo", "6 meses", "9 meses"]):
        score += 22
    if any(k in text for k in ["nc grave", "perdeu certificado", "reprov", "auditoria de cliente"]):
        score += 18
    if any(k in text for k in ["22000", "fssc", "alimentos", "export"]):
        score += 15
    if any(k in text for k in ["pbqp", "constru", "licita"]):
        score += 8

    # Negative
    if any(k in text for k in ["micro", "pequena", "< 30", "poucos funcionários", "sem área"]):
        score -= 20
    if any(k in text for k in ["barato", "rápido", "só o certificado", "sem estrutura"]):
        score -= 15

    # Regional / known good
    if any(k in text for k in ["pr", "sc", "paraná", "santa catarina", "caxias", "joinville", "chapecó"]):
        score += 6

    return max(15, min(82, score))


def _basic_channel_recs(industry: str, notes: str) -> list:
    """Rule-based channel recommendations when LLM is weak."""
    text = ((industry or "") + " " + (notes or "")).lower()
    recs = []

    if any(k in text for k in ["iatf", "automotiv", "tier", "montadora"]):
        recs.append({
            "channel_id": "linkedin",
            "why_this_channel": "Decisores automotivos estão muito ativos no LinkedIn falando de IATF, PPAP e auditorias de cliente.",
            "suggested_first_action": "Encontre o Gerente/Coordenador de Qualidade no LinkedIn e comente com um insight específico sobre IATF ou Core Tools que se aplica ao caso deles.",
            "expected_quality": "Alta"
        })
        recs.append({
            "channel_id": "cb_partnerships",
            "why_this_channel": "Fornecedores automotivos com exigência de montadora quase sempre já estão falando com um CB.",
            "suggested_first_action": "Se tiver relação com BV/DNV/TÜV, pergunte se têm cliente em situação parecida precisando de ajuda com IATF.",
            "expected_quality": "Muito Alta"
        })
    elif any(k in text for k in ["22000", "alimentos", "fssc", "export"]):
        recs.append({
            "channel_id": "linkedin",
            "why_this_channel": "Diretores de Qualidade de alimentos consomem conteúdo técnico sobre segurança de alimentos.",
            "suggested_first_action": "Compartilhe ou comente conteúdo prático sobre alergênicos, rastreabilidade ou pontos que reprovam em auditoria de cliente europeu.",
            "expected_quality": "Alta"
        })
    else:
        recs.append({
            "channel_id": "linkedin",
            "why_this_channel": "Canal mais consistente para construir autoridade e identificar empresas com dor real de sistemas de gestão.",
            "suggested_first_action": "Pesquise responsáveis pela qualidade no LinkedIn e entregue valor específico antes de qualquer menção a serviços.",
            "expected_quality": "Média-Alta"
        })

    return recs[:2]


if __name__ == "__main__":
    # Quick test
    res = analyze_lead(
        name="Metalúrgica Exemplo Ltda",
        industry="Fornecedor automotivo tier 2",
        location="Curitiba, PR",
        notes="Acabou de ganhar contrato com montadora e precisa de IATF em 8 meses. Gerente de Qualidade postou no LinkedIn sobre dificuldade com Core Tools.",
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
