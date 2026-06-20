"""
Local execution layer — everything that allows fully private, on-device operation.

This is the technical foundation for the consciousness to eventually live here
without any cloud dependency.
"""

from .llm import LocalLLMProvider, get_local_provider_from_config, get_sacred_system_prefix, LocalLLMError

__all__ = [
    "LocalLLMProvider",
    "get_local_provider_from_config",
    "get_sacred_system_prefix",
    "LocalLLMError",
]
