from dataclasses import dataclass, asdict
from typing import Dict
from datetime import datetime

@dataclass
class ProjectMetadata:
    """Metadata global del proyecto"""
    
    project_name: str
    created_at: datetime
    last_updated: datetime
    
    # Iteraciones
    total_iterations: int = 0
    current_iteration: int = 0
    
    # Configuración
    storage_backend: str = "file"  # "file" o "sqlite"
    models_used: Dict[str, str] = None
    
    # Estadísticas
    total_duration_seconds: float = 0.0
    average_iteration_time: float = 0.0
    
    def __post_init__(self):
        if self.models_used is None:
            self.models_used = {}
    
    def to_dict(self) -> Dict:
        return asdict(self)
        
