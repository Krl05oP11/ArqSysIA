# arqsysia/phases/__init__.py
"""
Módulo de fases del pipeline ArqSysIA.

Cada fase es un módulo independiente que procesa el estado del proyecto.
"""

from arqsysia.phases.base import BasePhase
from arqsysia.phases.analyzer import AnalyzerPhase
from arqsysia.phases.codegen import CodeGenPhase
from arqsysia.phases.validator import ValidatorPhase

__all__ = [
    'BasePhase',
    'AnalyzerPhase',
    'CodeGenPhase',
    'ValidatorPhase',
]

