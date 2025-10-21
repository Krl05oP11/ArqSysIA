"""
State Manager para ArqSysIA.

Gestiona el estado completo del proyecto durante el pipeline de análisis
arquitectural, incluyendo resultados de cada fase y metadata.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class PipelinePhase(Enum):
    """Fases del pipeline de ArqSysIA."""
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    ANALYSIS_COMPLETE = "analysis_complete"
    GENERATING = "generating"
    GENERATION_COMPLETE = "generation_complete"
    VALIDATING = "validating"
    VALIDATION_COMPLETE = "validation_complete"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseResult:
    """Resultado de una fase del pipeline."""
    phase: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    """Resultado de la Fase 1: Análisis."""
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    architecture_pattern: Optional[str] = None
    architecture_justification: Optional[str] = None
    tech_stack: Dict[str, str] = field(default_factory=dict)
    main_components: List[str] = field(default_factory=list)
    directory_structure: Optional[str] = None
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    mvp_scope: Optional[str] = None
    product_roadmap: Optional[str] = None


@dataclass
class GenerationResult:
    """Resultado de la Fase 2: Generación."""
    file_structure: Dict[str, Any] = field(default_factory=dict)
    generated_files: List[str] = field(default_factory=list)
    setup_scripts: List[str] = field(default_factory=list)
    documentation_files: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Resultado de la Fase 3: Validación."""
    inconsistencies: List[str] = field(default_factory=list)
    potential_errors: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    security_considerations: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)


@dataclass
class ProjectState:
    """
    Estado completo del proyecto durante el pipeline.
    
    Mantiene toda la información generada por cada fase,
    metadata temporal, y permite serialización/deserialización.
    """
# Identificación
    project_name: str
    
    # === Metadata de iteración (NUEVO para v1.0) ===
    iteration: int = 1
    parent_iteration: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # === Feedback context (NUEVO para v1.0) ===
    user_feedback: Optional[str] = None
    previous_issues: List[Dict] = field(default_factory=list)
    changes_from_previous: Optional[str] = None
    
    # Estado del pipeline
    current_phase: str = PipelinePhase.INITIALIZED.value
    
    # Input original
    original_requirements: str = ""
    
    # Resultados de cada fase
    analysis: Optional[AnalysisResult] = None
    generation: Optional[GenerationResult] = None
    validation: Optional[ValidationResult] = None
    
    # Metadata de ejecución de fases
    phase_results: List[PhaseResult] = field(default_factory=list)
    
    # Configuración usada
    model_config: Dict[str, str] = field(default_factory=dict)
    
    # Metadata adicional
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Outputs genéricos de las fases
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    def update_phase(self, phase: PipelinePhase):
        """Actualiza la fase actual del pipeline."""
        self.current_phase = phase.value
        self.updated_at = datetime.now().isoformat()
    
    def add_phase_result(self, result: PhaseResult):
        """Agrega resultado de una fase."""
        self.phase_results.append(result)
        self.updated_at = datetime.now().isoformat()
    def set_output(self, key: str, value: Any):
        """
        Establece un valor en los outputs del proyecto.
        
        Args:
            key: Clave del output
            value: Valor a guardar
        """
        self.outputs[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def get_output(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de los outputs del proyecto.
        
        Args:
            key: Clave del output
            default: Valor por defecto si no existe
            
        Returns:
            Valor del output o default
        """
        return self.outputs.get(key, default)
            
        """Establece resultado de análisis (Fase 1)."""
        self.analysis = analysis
        self.updated_at = datetime.now().isoformat()
    
    def set_generation_result(self, generation: GenerationResult):
        """Establece resultado de generación (Fase 2)."""
        self.generation = generation
        self.updated_at = datetime.now().isoformat()
    
    def set_validation_result(self, validation: ValidationResult):
        """Establece resultado de validación (Fase 3)."""
        self.validation = validation
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario."""
        data = asdict(self)
        
        # Convertir datetime a string para serialización JSON
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        return data
            
    def to_json(self, indent: int = 2) -> str:
        """Convierte el estado a JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_yaml(self) -> str:
        """Convierte el estado a YAML."""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
    
    def save_json(self, filepath: Path):
        """Guarda el estado como JSON."""
        filepath.write_text(self.to_json(), encoding='utf-8')
    
    def save_yaml(self, filepath: Path):
        """Guarda el estado como YAML."""
        filepath.write_text(self.to_yaml(), encoding='utf-8')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Crea ProjectState desde diccionario."""
        # Reconstruir objetos anidados
        if data.get('analysis'):
            data['analysis'] = AnalysisResult(**data['analysis'])
        if data.get('generation'):
            data['generation'] = GenerationResult(**data['generation'])
        if data.get('validation'):
            data['validation'] = ValidationResult(**data['validation'])
        
        # Reconstruir phase_results
        if data.get('phase_results'):
            data['phase_results'] = [
                PhaseResult(**pr) for pr in data['phase_results']
            ]
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProjectState':
        """Crea ProjectState desde JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'ProjectState':
        """Crea ProjectState desde YAML."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def load_json(cls, filepath: Path) -> 'ProjectState':
        """Carga ProjectState desde archivo JSON."""
        json_str = filepath.read_text(encoding='utf-8')
        return cls.from_json(json_str)
    
    @classmethod
    def load_yaml(cls, filepath: Path) -> 'ProjectState':
        """Carga ProjectState desde archivo YAML."""
        yaml_str = filepath.read_text(encoding='utf-8')
        return cls.from_yaml(yaml_str)


class StateManager:
    """
    Manager para gestionar el estado del proyecto.
    
    Proporciona interfaz simplificada para crear, actualizar,
    y persistir el estado del proyecto.
    """
    
    def __init__(self, output_dir: Union[str, Path] = "output"):
        """
        Inicializa el StateManager.
        
        Args:
            output_dir: Directorio donde guardar los estados (puede ser str o Path)
        """
        # Convertir a Path si es string
        if isinstance(output_dir, str):
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = output_dir
        
        # Crear directorio si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_state = None
    
    def create_project(
        self,
        project_name: str,
        requirements: str,
        model_config: Optional[Dict[str, str]] = None
    ) -> ProjectState:
        """
        Crea un nuevo proyecto.
        
        Args:
            project_name: Nombre del proyecto
            requirements: Requerimientos originales
            model_config: Configuración de modelos a usar
            
        Returns:
            ProjectState inicializado
        """
        state = ProjectState(
            project_name=project_name,
            original_requirements=requirements,
            model_config=model_config or {}
        )
        self.current_state = state
        return state
    
    def save_state(
        self,
        state: Optional[ProjectState] = None,
        format: str = "json",
        filename: Optional[str] = None
    ) -> Path:
        """
        Guarda el estado actual.
        
        Args:
            state: Estado a guardar (usa current_state si es None)
            format: Formato de salida ("json" o "yaml")
            filename: Nombre del archivo (opcional)
            
        Returns:
            Path del archivo guardado
        """
        state = state or self.current_state
        if not state:
            raise ValueError("No hay estado para guardar")
        
        # Generar nombre de archivo si no se especifica
        if filename is None:
            safe_name = state.project_name.lower().replace(" ", "_")
            filename = f"{safe_name}_state.{format}"
        
        filepath = self.output_dir / filename
        
        if format == "json":
            state.save_json(filepath)
        elif format == "yaml":
            state.save_yaml(filepath)
        else:
            raise ValueError(f"Formato no soportado: {format}")
        
        return filepath
    
    def load_state(
        self, 
        project_name: str,
        format: str = "json"
    ) -> ProjectState:
        """
        Carga estado desde archivo usando el nombre del proyecto.
        
        Args:
            project_name: Nombre del proyecto
            format: Formato del archivo ("json" o "yaml")
            
        Returns:
            ProjectState cargado
        """
        safe_name = project_name.lower().replace(" ", "_")
        filename = f"{safe_name}_state.{format}"
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
        
        if format == "json":
            state = ProjectState.load_json(filepath)
        elif format in ["yaml", "yml"]:
            state = ProjectState.load_yaml(filepath)
        else:
            raise ValueError(f"Formato no soportado: {format}")
        
        self.current_state = state
        return state
    
    def auto_save(self, format: str = "json"):
        """Guarda automáticamente el estado actual."""
        if self.current_state:
            return self.save_state(format=format)
        return None
        
