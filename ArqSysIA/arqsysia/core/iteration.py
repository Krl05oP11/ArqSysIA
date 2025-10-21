from dataclasses import dataclass, field, asdict
from typing import List, Dict
from datetime import datetime
from .state import ProjectState
from .decision import Decision

@dataclass
class Iteration:
    """Representa una iteración completa del proyecto"""
    
    project_name: str
    iteration_number: int
    state: ProjectState
    decisions: List[Decision] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    phase_durations: Dict[str, float] = field(default_factory=dict)
    
    # Scores
    final_scores: Dict[str, int] = field(default_factory=dict)
    
    # Status
    status: str = "completed"  # "completed", "in_progress", "failed"
    
    def to_dict(self) -> Dict:
        """Serialización completa"""
        # Convertir state a dict
        state_dict = self.state.to_dict()
        
        # Convertir created_at a string si es datetime
        created_at_str = self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
        
        return {
            "project_name": self.project_name,
            "iteration_number": self.iteration_number,
            "state": state_dict,
            "decisions": [d.to_dict() for d in self.decisions],
            "created_at": created_at_str,
            "duration_seconds": self.duration_seconds,
            "phase_durations": self.phase_durations,
            "final_scores": self.final_scores,
            "status": self.status
        }
        
