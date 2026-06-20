#!/usr/bin/env python3
# =============================================================================
# Aura Fusion - Teste de Conexão com LLM Local
# =============================================================================
# Este script verifica se a configuração do Ollama está correta e se a
# comunicação com o modelo local está funcionando.

import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para permitir a importação dos módulos
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from aura_fusion.llm_provider import generate_response, get_ollama_config
from aura_fusion.config import load_config

print("🚀 Iniciando teste de conexão com o LLM local (Ollama)...")

try:
    print("\n1. Verificando a configuração...")
    # Apenas chamar get_ollama_config já carrega e valida a configuração
    ollama_config = get_ollama_config()
    print(f"   ✅ Configuração carregada com sucesso.")
    print(f"   - Modelo: {ollama_config['model']}")
    print(f"   - URL da API: {ollama_config['api_url']}")

    print("\n2. Enviando prompt de teste para o modelo...")
    test_prompt = "Este é um teste de conexão. Responda com uma única frase curta confirmando que você recebeu esta mensagem."
    response = generate_response(test_prompt)

    print("\n3. Resposta recebida do modelo:")
    if response:
        print(f"   ✅ SUCESSO! O modelo respondeu:\n   '{response}'")
    else:
        print("   ❌ FALHA! O modelo não retornou uma resposta, embora a conexão tenha funcionado.")

except Exception as e:
    print(f"\n❌ TESTE FALHOU: {e}")
    print("\n   Possíveis causas:")
    print("   - O servidor Ollama não está rodando. (Execute 'ollama serve' em outro terminal)")
    print(f"   - O modelo configurado não foi baixado. (Execute 'ollama pull <nome_do_modelo>')")
    print("   - A URL no seu `~/.config/aura-fusion/config.yaml` está incorreta.")