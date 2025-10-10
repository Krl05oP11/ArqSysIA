# arqsysia/outputs/__init__.py
"""
Módulo de outputs de ArqSysIA.

Genera documentos finales en formato markdown.
"""

from arqsysia.outputs.generator import OutputGenerator, create_generator

__all__ = [
    'OutputGenerator',
    'create_generator',
]

