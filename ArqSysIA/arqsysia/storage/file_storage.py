"""
FileStorage Backend - Sistema de almacenamiento basado en archivos JSON
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from .base import StorageBackend
from ..core.iteration import Iteration
from ..core.decision import Decision
from ..core.metadata import ProjectMetadata


class FileStorage(StorageBackend):
    """
    Backend de almacenamiento basado en archivos JSON.
    
    Estructura de directorios:
    projects/
    └── {project_name}/
        ├── metadata.json
        ├── decisions_log.jsonl
        └── iterations/
            ├── iteration_001.json
            ├── iteration_002.json
            └── ...
    """
    
    def __init__(self, base_dir: str = "projects"):
        """
        Inicializa el FileStorage.
        
        Args:
            base_dir: Directorio base donde se almacenarán los proyectos
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_project_dir(self, project_name: str) -> Path:
        """Obtiene el directorio del proyecto"""
        return self.base_dir / project_name
    
    def _get_iterations_dir(self, project_name: str) -> Path:
        """Obtiene el directorio de iteraciones"""
        return self._get_project_dir(project_name) / "iterations"
    
    def _get_iteration_file(self, project_name: str, iteration_number: int) -> Path:
        """Obtiene la ruta del archivo de iteración"""
        return self._get_iterations_dir(project_name) / f"iteration_{iteration_number:03d}.json"
    
    def _get_metadata_file(self, project_name: str) -> Path:
        """Obtiene la ruta del archivo de metadata"""
        return self._get_project_dir(project_name) / "metadata.json"
    
    def _get_decisions_file(self, project_name: str) -> Path:
        """Obtiene la ruta del archivo de decisiones"""
        return self._get_project_dir(project_name) / "decisions_log.jsonl"
    
    def _ensure_project_structure(self, project_name: str) -> None:
        """Crea la estructura de directorios del proyecto si no existe"""
        project_dir = self._get_project_dir(project_name)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        iterations_dir = self._get_iterations_dir(project_name)
        iterations_dir.mkdir(parents=True, exist_ok=True)
        
    # ============================================================
    # MÉTODOS DE ITERACIONES
    # ============================================================
    
    def save_iteration(self, iteration: Iteration) -> None:
        """
        Guarda una iteración completa.
        
        Args:
            iteration: Objeto Iteration a guardar
        """
        self._ensure_project_structure(iteration.project_name)
        
        iteration_file = self._get_iteration_file(
            iteration.project_name, 
            iteration.iteration_number
        )
        
        # Serializar a JSON
        data = iteration.to_dict()
        
        # Guardar archivo
        with open(iteration_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Actualizar metadata
        self._update_metadata_on_save(iteration)
    
    def load_iteration(self, project_name: str, iteration_number: int) -> Optional[Iteration]:
        """
        Carga una iteración específica.
        
        Args:
            project_name: Nombre del proyecto
            iteration_number: Número de iteración
            
        Returns:
            Objeto Iteration o None si no existe
        """
        iteration_file = self._get_iteration_file(project_name, iteration_number)
        
        if not iteration_file.exists():
            return None
        
        with open(iteration_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruir objeto Iteration
        return self._dict_to_iteration(data)
    
    def list_iterations(self, project_name: str) -> List[Dict]:
        """
        Lista todas las iteraciones de un proyecto.
        
        Args:
            project_name: Nombre del proyecto
            
        Returns:
            Lista de diccionarios con información básica de cada iteración
        """
        iterations_dir = self._get_iterations_dir(project_name)
        
        if not iterations_dir.exists():
            return []
        
        iterations = []
        for iteration_file in sorted(iterations_dir.glob("iteration_*.json")):
            with open(iteration_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extraer info básica
            iterations.append({
                "iteration_number": data["iteration_number"],
                "created_at": data["created_at"],
                "duration_seconds": data["duration_seconds"],
                "status": data["status"],
                "final_scores": data.get("final_scores", {})
            })
        
        return iterations
    
    def delete_iteration(self, project_name: str, iteration_number: int) -> None:
        """
        Elimina una iteración (para rollback).
        
        Args:
            project_name: Nombre del proyecto
            iteration_number: Número de iteración a eliminar
        """
        iteration_file = self._get_iteration_file(project_name, iteration_number)
        
        if iteration_file.exists():
            iteration_file.unlink()
            
        # Actualizar metadata
        self._update_metadata_on_delete(project_name, iteration_number)

    # ============================================================
    # MÉTODOS DE DECISIONES
    # ============================================================
    
    def save_decision(self, project_name: str, decision: Decision) -> None:
        """
        Guarda una decisión en el log (append-only).
        
        Args:
            project_name: Nombre del proyecto
            decision: Objeto Decision a guardar
        """
        self._ensure_project_structure(project_name)
        
        decisions_file = self._get_decisions_file(project_name)
        
        # Serializar a JSON (una línea)
        data = decision.to_dict()
        
        # Append al archivo JSONL
        with open(decisions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def get_decisions(
        self, 
        project_name: str, 
        iteration: Optional[int] = None
    ) -> List[Decision]:
        """
        Obtiene decisiones del proyecto.
        
        Args:
            project_name: Nombre del proyecto
            iteration: Número de iteración (opcional, None = todas)
            
        Returns:
            Lista de objetos Decision
        """
        decisions_file = self._get_decisions_file(project_name)
        
        if not decisions_file.exists():
            return []
        
        decisions = []
        with open(decisions_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    
                    # Filtrar por iteración si se especifica
                    if iteration is None or data["iteration"] == iteration:
                        decisions.append(self._dict_to_decision(data))
        
        return decisions
    # ============================================================
    # MÉTODOS DE METADATA
    # ============================================================
    
    def save_metadata(self, metadata: ProjectMetadata) -> None:
        """
        Guarda metadata del proyecto.
        
        Args:
            metadata: Objeto ProjectMetadata
        """
        self._ensure_project_structure(metadata.project_name)
        
        metadata_file = self._get_metadata_file(metadata.project_name)
        
        data = metadata.to_dict()
        
        # Convertir datetime a string
        data['created_at'] = data['created_at'].isoformat() if isinstance(data['created_at'], datetime) else data['created_at']
        data['last_updated'] = data['last_updated'].isoformat() if isinstance(data['last_updated'], datetime) else data['last_updated']
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_metadata(self, project_name: str) -> Optional[ProjectMetadata]:
        """
        Carga metadata del proyecto.
        
        Args:
            project_name: Nombre del proyecto
            
        Returns:
            Objeto ProjectMetadata o None si no existe
        """
        metadata_file = self._get_metadata_file(project_name)
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruir objeto
        return self._dict_to_metadata(data)
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def _update_metadata_on_save(self, iteration: Iteration) -> None:
        """Actualiza metadata cuando se guarda una iteración"""
        metadata = self.load_metadata(iteration.project_name)
        
        if metadata is None:
            # Crear metadata inicial
            metadata = ProjectMetadata(
                project_name=iteration.project_name,
                created_at=iteration.created_at,
                last_updated=iteration.created_at,
                total_iterations=1,
                current_iteration=iteration.iteration_number,
                storage_backend="file",
                total_duration_seconds=iteration.duration_seconds,  # FIX: Inicializar con la duración
                average_iteration_time=iteration.duration_seconds   # FIX: Primera iteración = promedio
            )
        else:
            # Actualizar metadata existente
            metadata.last_updated = datetime.now()
            metadata.total_iterations = max(metadata.total_iterations, iteration.iteration_number)
            metadata.current_iteration = iteration.iteration_number
            metadata.total_duration_seconds += iteration.duration_seconds
            
            if metadata.total_iterations > 0:
                metadata.average_iteration_time = (
                    metadata.total_duration_seconds / metadata.total_iterations
                )
        
        self.save_metadata(metadata)
            
    def _update_metadata_on_delete(self, project_name: str, iteration_number: int) -> None:
        """Actualiza metadata cuando se elimina una iteración"""
        metadata = self.load_metadata(project_name)
        
        if metadata:
            # Recontamos las iteraciones existentes
            iterations = self.list_iterations(project_name)
            metadata.total_iterations = len(iterations)
            
            if iterations:
                metadata.current_iteration = max(i["iteration_number"] for i in iterations)
            else:
                metadata.current_iteration = 0
            
            metadata.last_updated = datetime.now()
            self.save_metadata(metadata)
    
    def _dict_to_iteration(self, data: Dict) -> Iteration:
        """Convierte diccionario a objeto Iteration"""
        from ..core.state import ProjectState
        
        # Reconstruir ProjectState
        state_data = data["state"]
        state = ProjectState(**state_data)
        
        # Reconstruir Decisions
        decisions = [self._dict_to_decision(d) for d in data["decisions"]]
        
        # Reconstruir Iteration
        return Iteration(
            project_name=data["project_name"],
            iteration_number=data["iteration_number"],
            state=state,
            decisions=decisions,
            created_at=datetime.fromisoformat(data["created_at"]),
            duration_seconds=data["duration_seconds"],
            phase_durations=data.get("phase_durations", {}),
            final_scores=data.get("final_scores", {}),
            status=data.get("status", "completed")
        )
    
    def _dict_to_decision(self, data: Dict) -> Decision:
        """Convierte diccionario a objeto Decision"""
        return Decision(
            iteration=data["iteration"],
            phase=data["phase"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            decision=data.get("decision", ""),
            rationale=data.get("rationale", ""),
            alternatives_considered=data.get("alternatives_considered", []),
            chosen_alternative=data.get("chosen_alternative", ""),
            impacted_components=data.get("impacted_components", []),
            triggered_by=data.get("triggered_by", "manual")
        )
    
    def _dict_to_metadata(self, data: Dict) -> ProjectMetadata:
        """Convierte diccionario a objeto ProjectMetadata"""
        return ProjectMetadata(
            project_name=data["project_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            total_iterations=data.get("total_iterations", 0),
            current_iteration=data.get("current_iteration", 0),
            storage_backend=data.get("storage_backend", "file"),
            models_used=data.get("models_used", {}),
            total_duration_seconds=data.get("total_duration_seconds", 0.0),
            average_iteration_time=data.get("average_iteration_time", 0.0)
        )

