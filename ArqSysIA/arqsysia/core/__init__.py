# arqsysia/core/__init__.py
"""
Módulo core de ArqSysIA.

Contiene componentes centrales: Estado, Orquestador, Configuración.
"""

from arqsysia.core.state import ProjectState, StateManager
from arqsysia.core.orchestrator import PipelineOrchestrator, create_orchestrator

__all__ = [
    'ProjectState',
    'StateManager',
    'PipelineOrchestrator',
    'create_orchestrator',
]

