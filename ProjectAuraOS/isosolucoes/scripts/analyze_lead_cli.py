#!/usr/bin/env python3
"""
Quick CLI for analyzing a lead with the IsoSoluções specialized model.
Useful for terminal / Sofia integration.

Usage:
    python scripts/analyze_lead_cli.py "Nome da Empresa" --industry "Fornecedor automotivo" --notes "Ganhou contrato e precisa de IATF"
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import analyze_lead, is_ollama_available
from core.db import create_company, save_analysis

def main():
    parser = argparse.ArgumentParser(description="IsoSoluções lead analyzer (local LLM)")
    print("Ollama local disponível:" , "SIM" if is_ollama_available() else "NÃO (fallback)")
    parser.add_argument("name", help="Nome da empresa")
    parser.add_argument("--website", default="")
    parser.add_argument("--industry", default="")
    parser.add_argument("--location", default="")
    parser.add_argument("--size", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--save", action="store_true", help="Salvar no banco de leads do IsoCanal")
    args = parser.parse_args()

    result = analyze_lead(
        name=args.name,
        website=args.website or None,
        industry=args.industry or None,
        location=args.location or None,
        size_estimate=args.size or None,
        notes=args.notes or None,
        model=args.model,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.save:
        cid = create_company(
            name=args.name,
            website=args.website or None,
            industry=args.industry or None,
            location=args.location or None,
            size_estimate=args.size or None,
            notes=args.notes or None,
        )
        save_analysis(cid, result)
        print(f"\n[Saved] company_id={cid}")

if __name__ == "__main__":
    main()
