"""
Módulo de clientes para interactuar con backends de IA.
"""

from .ollama_client import OllamaClient, OllamaConfig, OllamaClientError, create_client

__all__ = [
    'OllamaClient',
    'OllamaConfig',
    'OllamaClientError',
    'create_client',
]
