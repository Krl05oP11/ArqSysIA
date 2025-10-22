"""
VersionManager - Gestor de versiones e iteraciones del proyecto
"""
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from arqsysia.storage.base import StorageBackend
from arqsysia.core.state import Iteration, ProjectState, Decision, ProjectMetadata

if TYPE_CHECKING:
    from arqsysia.storage.file_storage import FileStorage


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
        
        # Import lazy para evitar circular import
        if storage is None:
            from arqsysia.storage.file_storage import FileStorage
            storage = FileStorage(base_dir=base_dir)
        
        self.storage = storage
    
    # ============================================================
    # OPERACIONES BÁSICAS
    # ============================================================
    
    def save_iteration(
        self,
        state: ProjectState,
        decisions: List[Decision] = None,
        duration: float = 0.0,
        phase_durations: Dict[str, float] = None
    ) -> Iteration:
        """
        Guarda una nueva iteración.
        
        Args:
            state: Estado del proyecto en esta iteración
            decisions: Lista de decisiones tomadas
            duration: Duración total en segundos
            phase_durations: Duración por fase
            
        Returns:
            Iteration guardada
        """
        if decisions is None:
            decisions = []
        if phase_durations is None:
            phase_durations = {}
        
        # Extraer scores del estado
        final_scores = state.outputs.get("validation", {}).get("scores", {})
        
        # Crear objeto Iteration
        iteration = Iteration(
            project_name=self.project_name,
            iteration_number=state.iteration,
            state=state,
            decisions=decisions,
            created_at=state.created_at,
            duration_seconds=duration,
            phase_durations=phase_durations,
            final_scores=final_scores,
            status="completed"
        )
        
        # Guardar usando el storage
        self.storage.save_iteration(iteration)
        
        return iteration
    
    def get_iteration(self, iteration_number: int) -> Iteration:
        """
        Obtiene una iteración específica.
        
        Args:
            iteration_number: Número de iteración
            
        Returns:
            Iteration
            
        Raises:
            FileNotFoundError: Si la iteración no existe
        """
        try:
            iteration = self.storage.load_iteration(self.project_name, iteration_number)
            if iteration is None:
                raise FileNotFoundError(f"Iteration {iteration_number} not found in project {self.project_name}")
            return iteration
        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileNotFoundError(f"Iteration {iteration_number} not found: {str(e)}")
    
    def list_iterations(self) -> List[Iteration]:
        """
        Lista todas las iteraciones del proyecto.
        
        Returns:
            Lista de objetos Iteration
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
    
        # Encontrar la iteración con el número más alto
        latest_number = max(i.iteration_number for i in iterations)
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
        Compara dos iteraciones.
        
        Args:
            iteration_a: Número de primera iteración
            iteration_b: Número de segunda iteración
            
        Returns:
            Diccionario con diferencias detalladas
        """
        iter_a = self.get_iteration(iteration_a)
        iter_b = self.get_iteration(iteration_b)
        
        # Comparar arquitectura
        arch_a = iter_a.state.outputs.get("analysis", {}).get("architecture", "")
        arch_b = iter_b.state.outputs.get("analysis", {}).get("architecture", "")
        
        architecture_changed = {
            "changed": arch_a != arch_b,
            "previous": arch_a,
            "current": arch_b
        }
        
        # Comparar componentes
        comps_a = set(iter_a.state.outputs.get("analysis", {}).get("components", []))
        comps_b = set(iter_b.state.outputs.get("analysis", {}).get("components", []))
        
        components_changed = {
            "added": list(comps_b - comps_a),
            "removed": list(comps_a - comps_b),
            "modified": []  # Básico por ahora
        }
        
        # Calcular diferencias en scores
        scores_diff = {}
        if iter_a.final_scores and iter_b.final_scores:
            all_keys = set(iter_a.final_scores.keys()) | set(iter_b.final_scores.keys())
            for key in all_keys:
                score_a = iter_a.final_scores.get(key, 0)
                score_b = iter_b.final_scores.get(key, 0)
                scores_diff[key] = score_b - score_a
        
        return {
            "architecture_changed": architecture_changed,
            "components_changed": components_changed,
            "scores_diff": scores_diff
        }
    
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
            return  # No hay nada que hacer
            # raise ValueError("No hay iteraciones para hacer rollback")
        
        # Verificar que la iteración existe
        if not self.get_iteration(iteration_number):
            raise ValueError(f"La iteración {iteration_number} no existe")
        
        # Eliminar todas las iteraciones posteriores
        for iteration in iterations:
            if iteration.iteration_number > iteration_number:
                self.storage.delete_iteration(self.project_name, iteration.iteration_number)
                    
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
        
