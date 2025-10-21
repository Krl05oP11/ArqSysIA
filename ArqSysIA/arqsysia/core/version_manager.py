"""
VersionManager - Gestor de versiones e iteraciones del proyecto
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from ..storage.base import StorageBackend
from ..storage.file_storage import FileStorage
from .iteration import Iteration
from .decision import Decision
from .metadata import ProjectMetadata


class VersionManager:
    """
    Gestor de alto nivel para manejar versiones e iteraciones del proyecto.
    
    Proporciona una interfaz simplificada sobre el StorageBackend para:
    - Guardar y recuperar iteraciones
    - Navegar por el historial
    - Comparar versiones
    - Rollback a versiones anteriores
    """
    
    def __init__(
        self, 
        project_name: str,
        storage: Optional[StorageBackend] = None,
        base_dir: str = "projects"
    ):
        """
        Inicializa el VersionManager.
        
        Args:
            project_name: Nombre del proyecto
            storage: Backend de almacenamiento (usa FileStorage por defecto)
            base_dir: Directorio base para proyectos
        """
        self.project_name = project_name
        self.storage = storage or FileStorage(base_dir=base_dir)
    
    # ============================================================
    # OPERACIONES BÁSICAS
    # ============================================================
    
    def save_iteration(self, iteration: Iteration) -> None:
        """
        Guarda una iteración.
        
        Args:
            iteration: Iteración a guardar
        """
        if iteration.project_name != self.project_name:
            raise ValueError(
                f"Project name mismatch: expected '{self.project_name}', "
                f"got '{iteration.project_name}'"
            )
        
        self.storage.save_iteration(iteration)
    
    def get_iteration(self, iteration_number: int) -> Optional[Iteration]:
        """
        Obtiene una iteración específica.
        
        Args:
            iteration_number: Número de iteración
            
        Returns:
            Iteration o None si no existe
        """
        return self.storage.load_iteration(self.project_name, iteration_number)
    
    def list_iterations(self) -> List[Dict]:
        """
        Lista todas las iteraciones del proyecto.
        
        Returns:
            Lista de diccionarios con info básica de cada iteración
        """
        return self.storage.list_iterations(self.project_name)
    
    def get_latest_iteration(self) -> Optional[Iteration]:
        """
        Obtiene la última iteración del proyecto.
        
        Returns:
            Iteration más reciente o None si no hay iteraciones
        """
        iterations = self.list_iterations()
        
        if not iterations:
            return None
        
        # Obtener el número de la última iteración
        latest_number = max(i["iteration_number"] for i in iterations)
        
        return self.get_iteration(latest_number)
    
    def get_metadata(self) -> Optional[ProjectMetadata]:
        """
        Obtiene la metadata del proyecto.
        
        Returns:
            ProjectMetadata o None si no existe
        """
        return self.storage.load_metadata(self.project_name)
    
    # ============================================================
    # OPERACIONES DE COMPARACIÓN
    # ============================================================
    
    def compare_iterations(
        self, 
        iteration_a: int, 
        iteration_b: int
    ) -> Dict[str, Any]:
        """
        Compara dos iteraciones (versión básica).
        
        Args:
            iteration_a: Número de primera iteración
            iteration_b: Número de segunda iteración
            
        Returns:
            Diccionario con diferencias básicas
        """
        iter_a = self.get_iteration(iteration_a)
        iter_b = self.get_iteration(iteration_b)
        
        if not iter_a or not iter_b:
            raise ValueError("Una o ambas iteraciones no existen")
        
        # Comparación básica
        diff = {
            "iteration_a": iteration_a,
            "iteration_b": iteration_b,
            "duration_diff": iter_b.duration_seconds - iter_a.duration_seconds,
            "scores_a": iter_a.final_scores,
            "scores_b": iter_b.final_scores,
            "scores_changed": iter_a.final_scores != iter_b.final_scores,
            "requirements_changed": (
                iter_a.state.original_requirements != 
                iter_b.state.original_requirements
            ),
            "decisions_count_a": len(iter_a.decisions),
            "decisions_count_b": len(iter_b.decisions),
        }
        
        # Calcular diferencias en scores
        if iter_a.final_scores and iter_b.final_scores:
            score_diffs = {}
            all_keys = set(iter_a.final_scores.keys()) | set(iter_b.final_scores.keys())
            
            for key in all_keys:
                score_a = iter_a.final_scores.get(key, 0)
                score_b = iter_b.final_scores.get(key, 0)
                score_diffs[key] = score_b - score_a
            
            diff["score_diffs"] = score_diffs
        
        return diff
    
    def compare_with_latest(self, iteration_number: int) -> Dict[str, Any]:
        """
        Compara una iteración con la última.
        
        Args:
            iteration_number: Número de iteración a comparar
            
        Returns:
            Diccionario con diferencias
        """
        latest = self.get_latest_iteration()
        
        if not latest:
            raise ValueError("No hay iteraciones en el proyecto")
        
        return self.compare_iterations(iteration_number, latest.iteration_number)
    
    # ============================================================
    # OPERACIONES DE ROLLBACK
    # ============================================================
    
    def rollback_to(self, iteration_number: int) -> None:
        """
        Hace rollback eliminando iteraciones posteriores.
        
        Args:
            iteration_number: Número de iteración a la cual volver
        """
        iterations = self.list_iterations()
        
        if not iterations:
            raise ValueError("No hay iteraciones para hacer rollback")
        
        # Verificar que la iteración existe
        if not self.get_iteration(iteration_number):
            raise ValueError(f"La iteración {iteration_number} no existe")
        
        # Eliminar todas las iteraciones posteriores
        for iter_info in iterations:
            if iter_info["iteration_number"] > iteration_number:
                self.storage.delete_iteration(
                    self.project_name, 
                    iter_info["iteration_number"]
                )
    
    def delete_iteration(self, iteration_number: int) -> None:
        """
        Elimina una iteración específica.
        
        Args:
            iteration_number: Número de iteración a eliminar
        """
        self.storage.delete_iteration(self.project_name, iteration_number)
    
    # ============================================================
    # OPERACIONES DE DECISIONES
    # ============================================================
    
    def save_decision(self, decision: Decision) -> None:
        """
        Guarda una decisión.
        
        Args:
            decision: Decision a guardar
        """
        self.storage.save_decision(self.project_name, decision)
    
    def get_decisions(self, iteration: Optional[int] = None) -> List[Decision]:
        """
        Obtiene decisiones del proyecto.
        
        Args:
            iteration: Número de iteración (None = todas)
            
        Returns:
            Lista de decisiones
        """
        return self.storage.get_decisions(self.project_name, iteration)
    
    # ============================================================
    # UTILIDADES
    # ============================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado del proyecto.
        
        Returns:
            Diccionario con información resumida
        """
        metadata = self.get_metadata()
        iterations = self.list_iterations()
        latest = self.get_latest_iteration()
        
        summary = {
            "project_name": self.project_name,
            "total_iterations": len(iterations),
            "has_iterations": len(iterations) > 0,
        }
        
        if metadata:
            summary.update({
                "created_at": metadata.created_at.isoformat(),
                "last_updated": metadata.last_updated.isoformat(),
                "total_duration_seconds": metadata.total_duration_seconds,
                "average_iteration_time": metadata.average_iteration_time,
                "storage_backend": metadata.storage_backend,
            })
        
        if latest:
            summary.update({
                "latest_iteration": latest.iteration_number,
                "latest_status": latest.status,
                "latest_scores": latest.final_scores,
            })
        
        return summary
    
    def exists(self) -> bool:
        """
        Verifica si el proyecto existe.
        
        Returns:
            True si el proyecto tiene al menos una iteración
        """
        return len(self.list_iterations()) > 0
        
