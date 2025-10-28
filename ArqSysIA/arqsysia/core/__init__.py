"""
Core module for ArqSysIA.

This module contains the core components for managing project state,
iterations, decisions, and version control.
"""

from .state import ProjectState, Iteration, Decision, ProjectMetadata
from .version_manager import VersionManager
from .decision_logger import DecisionLogger
from .diff_engine import DiffEngine, DiffResult

__all__ = [
    'ProjectState',
    'Iteration',
    'Decision',
    'ProjectMetadata',
    'VersionManager',
    'DecisionLogger',
    'DiffEngine',
    'DiffResult',
]
