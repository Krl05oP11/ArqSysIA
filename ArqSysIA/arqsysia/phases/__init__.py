"""
Módulo de fases del pipeline ArqSysIA.

Contiene las tres fases principales:
- Analyzer: Análisis arquitectural
- CodeGen: Generación de código y estructura
- Validator: Validación y mejoras
"""

from .base import BasePhase
from .analyzer import AnalyzerPhase, create_analyzer

__all__ = [
    'BasePhase',
    'AnalyzerPhase',
    'create_analyzer',
]

