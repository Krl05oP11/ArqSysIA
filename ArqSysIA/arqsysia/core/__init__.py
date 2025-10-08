"""
Módulo core de ArqSysIA.

Contiene componentes centrales: State Manager, Orchestrator, etc.
"""

from .state import (
    ProjectState,
    StateManager,
    PipelinePhase,
    PhaseResult,
    AnalysisResult,
    GenerationResult,
    ValidationResult,
)

__all__ = [
    'ProjectState',
    'StateManager',
    'PipelinePhase',
    'PhaseResult',
    'AnalysisResult',
    'GenerationResult',
    'ValidationResult',
]

