# =============================================================================
# Aura Fusion - Provedor de LLM (Ollama)
# =============================================================================
# Implementação real que se comunica com um servidor Ollama local.

import httpx
import json
from functools import lru_cache
from aura_fusion.config import load_config


@lru_cache(maxsize=1)
def get_ollama_config() -> dict:
    """
    Carrega a configuração do Ollama do arquivo e a armazena em cache.
    A função só lerá o arquivo do disco na primeira vez que for chamada.
    """
    print("[DEBUG: Carregando configuração do Ollama...]")
    app_config = load_config()

    if not app_config.local_model or not app_config.local_model.enabled:
        raise ConnectionError("Ollama não está habilitado no arquivo de configuração.")
    if app_config.local_model.provider != "ollama":
        raise ValueError(f"Provedor de LLM configurado é '{app_config.local_model.provider}', mas o código espera 'ollama'.")

    return {
        "api_url": f"{app_config.local_model.base_url}/api/generate",
        "model": app_config.local_model.model,
        "temperature": app_config.local_model.temperature,
    }


def generate_response(full_prompt: str) -> str:
    """
    Envia um prompt para o LLM local (Ollama) e retorna a resposta.
    """
    try:
        ollama_config = get_ollama_config()

        # O prompt já contém o system prompt, então o enviamos diretamente.
        payload = {
            "model": ollama_config["model"],
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": ollama_config["temperature"]
            }
        }

        print(f"\n[DEBUG: Enviando prompt para {ollama_config['model']} via Ollama...]\n")
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(ollama_config["api_url"], json=payload)
            response.raise_for_status()  # Lança exceção para erros HTTP 4xx/5xx

            response_data = response.json()
            return response_data.get("response", "").strip()

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Adiciona contexto ao erro de conexão e o relança.
        # A CLI principal (cli.py) é responsável por capturar e exibir o erro ao usuário.
        raise ConnectionError(f"Falha ao comunicar com o servidor Ollama em {ollama_config.get('api_url', 'URL desconhecida')}: {e}") from e