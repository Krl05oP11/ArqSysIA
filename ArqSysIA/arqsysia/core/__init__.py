"""
Core module for ArqSysIA.

This module contains the core components for managing project state,
iterations, decisions, and version control.
"""

from .state import ProjectState, Iteration, Decision, ProjectMetadata
from .version_manager import VersionManager
from .decision_logger import DecisionLogger
from .diff_engine import DiffEngine, DiffResult
from .iterative_orchestrator import (
    IterativeOrchestrator,
    IterationResult,
    create_iterative_orchestrator
)

__all__ = [
    # State management
    'ProjectState',
    'Iteration',
    'Decision',
    'ProjectMetadata',
    
    # Core components
    'VersionManager',
    'DecisionLogger',
    'DiffEngine',
    'DiffResult',
    
    # Orchestration
    'IterativeOrchestrator',
    'IterationResult',
    'create_iterative_orchestrator',
]

