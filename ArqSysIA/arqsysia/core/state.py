"""
arqsysia/core/state.py

Modelos de datos para ArqSysIA v1.0
- ProjectState: Estado completo del proyecto en una iteración
- Iteration: Representa una iteración completa con metadata
- Decision: Decisión arquitectónica documentada
- ProjectMetadata: Metadata del proyecto completo
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================
# ProjectState v2.0 (Enhanced para v1.0)
# ============================================

@dataclass
class ProjectState:
    """Estado completo del proyecto en una iteración"""
    
    # === Metadata de iteración (NUEVO en v1.0) ===
    project_name: str = ""
    iteration: int = 1
    parent_iteration: Optional[int] = None  # Para rastrear de dónde viene
    created_at: datetime = field(default_factory=datetime.now)
    
    # === Input original ===
    original_requirements: str = ""
    
    # === Outputs de fases ===
    outputs: Dict[str, Any] = field(default_factory=dict)
    # outputs["analysis"] = {...}
    # outputs["code_generation"] = {...}
    # outputs["validation"] = {...}
    
    # === Feedback context (NUEVO en v1.0) ===
    user_feedback: Optional[str] = None
    previous_issues: List[Dict] = field(default_factory=list)
    changes_from_previous: Optional[str] = None  # "Cambié X por Y porque..."
    
    # === Metadata de ejecución ===
    execution_metrics: Dict[str, float] = field(default_factory=dict)
    # {"analyzer_time": 312.5, "codegen_time": 803.2, ...}
    
    def to_dict(self) -> Dict:
        """Serialización completa del estado"""
        data = asdict(self)
        # Convertir datetime a string ISO
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data

# ============================================
# Iteration (NUEVO en v1.0)
# ============================================

@dataclass
class Iteration:
    """Representa una iteración completa del proyecto"""
    
    project_name: str
    iteration_number: int
    state: ProjectState
    decisions: List['Decision']
    
    # Metadata
    created_at: datetime
    duration_seconds: float
    phase_durations: Dict[str, float]  # {"analyzer": 312.5, ...}
    
    # Scores
    final_scores: Dict[str, int]  # {"architecture": 8, "code": 7, ...}
    
    # Status
    status: str = "completed"  # "completed", "in_progress", "failed"
    
    def to_dict(self) -> Dict:
        """Serialización completa"""
        return {
            "project_name": self.project_name,
            "iteration_number": self.iteration_number,
            "state": self.state.to_dict(),
            "decisions": [d.to_dict() for d in self.decisions],
            "created_at": self.created_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "phase_durations": self.phase_durations,
            "final_scores": self.final_scores,
            "status": self.status
        }


# ============================================
# Decision (NUEVO en v1.0)
# ============================================

@dataclass
class Decision:
    """Decisión arquitectónica documentada"""
    
    # Context (campos obligatorios primero)
    iteration: int
    phase: str  # "analyzer", "codegen", "validator"
    decision: str  # "Usar arquitectura de microservicios"
    rationale: str  # "Mejor escalabilidad y mantenimiento"
    
    # Campos opcionales después
    timestamp: datetime = field(default_factory=datetime.now)
    alternatives_considered: List[str] = field(default_factory=list)
    chosen_alternative: str = ""
    impacted_components: List[str] = field(default_factory=list)
    triggered_by: str = ""  # "user_feedback", "validation_issues", etc.
    
    def to_dict(self) -> Dict:
        """Serialización completa"""
        return {
            "iteration": self.iteration,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "decision": self.decision,
            "rationale": self.rationale,
            "alternatives_considered": self.alternatives_considered,
            "chosen_alternative": self.chosen_alternative,
            "impacted_components": self.impacted_components,
            "triggered_by": self.triggered_by
        }

# ============================================
# ProjectMetadata (NUEVO en v1.0)
# ============================================

@dataclass
class ProjectMetadata:
    """Metadata del proyecto completo"""
    
    project_name: str
    created_at: datetime
    last_updated: datetime
    
    # Iteration tracking
    total_iterations: int = 0
    current_iteration: int = 0
    
    # Storage info
    storage_backend: str = "file"  # "file" o "sqlite"
    storage_path: str = ""
    
    # Stats
    total_decisions: int = 0
    
    def to_dict(self) -> Dict:
        """Serialización completa"""
        return {
            "project_name": self.project_name,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "total_iterations": self.total_iterations,
            "current_iteration": self.current_iteration,
            "storage_backend": self.storage_backend,
            "storage_path": self.storage_path,
            "total_decisions": self.total_decisions
        }        
