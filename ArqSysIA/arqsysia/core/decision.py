from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class Decision:
    """Representa una decisión arquitectónica o de código"""
    
    iteration: int
    phase: str  # "analyzer", "codegen", "validator"
    timestamp: datetime = field(default_factory=datetime.now)
    
    # La decisión
    decision: str = ""
    rationale: str = ""
    
    # Contexto
    alternatives_considered: List[str] = field(default_factory=list)
    chosen_alternative: str = ""
    
    # Impacto
    impacted_components: List[str] = field(default_factory=list)
    
    # Metadata
    triggered_by: str = "manual"  # "user_feedback", "validator_issues", "manual"
    
    def to_dict(self) -> Dict:
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
        
