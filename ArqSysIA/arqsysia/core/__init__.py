"""
arqsysia/core/__init__.py

Exporta los componentes principales del core de ArqSysIA v1.0
"""

from .state import ProjectState, Iteration, Decision, ProjectMetadata
from .orchestrator import PipelineOrchestrator as Orchestrator
from .version_manager import VersionManager

__all__ = [
    'ProjectState',
    'Iteration',
    'Decision',
    'ProjectMetadata',
    'Orchestrator',
    'VersionManager'  # ← NUEVO - Sesión 8
]

