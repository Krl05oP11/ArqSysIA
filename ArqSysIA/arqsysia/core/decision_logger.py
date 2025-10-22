"""
DecisionLogger - Sistema de registro append-only de decisiones arquitectónicas.

Este módulo gestiona el registro y consulta de decisiones tomadas durante
el proceso iterativo de arquitectura de software.
"""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from arqsysia.storage.base import StorageBackend

from arqsysia.core.state import Decision


class DecisionLogger:
    """
    Gestiona el registro y consulta de decisiones arquitectónicas.
    
    Características:
    - Registro append-only (las decisiones no se modifican)
    - Vinculación a iteraciones específicas
    - Queries por iteración, fase, o búsqueda de texto
    - Persistencia vía StorageBackend
    
    Attributes:
        project_name: Nombre del proyecto
        storage: Backend de almacenamiento (FileStorage por defecto)
    """
    
    def __init__(
        self,
        project_name: str,
        storage: Optional['StorageBackend'] = None
    ):
        """
        Inicializa el DecisionLogger.
        
        Args:
            project_name: Nombre del proyecto
            storage: Backend de almacenamiento (opcional, usa FileStorage por defecto)
        """
        self.project_name = project_name
        
        # Import lazy para evitar circular imports
        if storage is None:
            from arqsysia.storage.file_storage import FileStorage
            self.storage = FileStorage()
        else:
            self.storage = storage
    
    def log_decision(
        self,
        iteration: int,
        phase: str,
        decision: str,
        rationale: str,
        alternatives_considered: Optional[List[str]] = None,
        chosen_alternative: Optional[str] = None,
        impacted_components: Optional[List[str]] = None,
        triggered_by: Optional[str] = None
    ) -> Decision:
        """
        Registra una nueva decisión arquitectónica.
        
        Este método crea una decisión con timestamp automático y la persiste
        en el log append-only.
        
        Args:
            iteration: Número de iteración donde se tomó la decisión
            phase: Fase donde se tomó la decisión (analyzer, codegen, validator)
            decision: Descripción de la decisión tomada
            rationale: Justificación de la decisión
            alternatives_considered: Lista de alternativas consideradas (opcional)
            chosen_alternative: Alternativa elegida (opcional)
            impacted_components: Componentes afectados (opcional)
            triggered_by: Qué provocó la decisión (opcional, ej: "validator", "user_feedback")
        
        Returns:
            Decision: Objeto Decision creado y guardado
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> decision = logger.log_decision(
            ...     iteration=2,
            ...     phase="analyzer",
            ...     decision="Cambiar de monolito a microservicios",
            ...     rationale="Mejorar escalabilidad y mantenibilidad",
            ...     alternatives_considered=["Monolito modular", "Microservicios"],
            ...     chosen_alternative="Microservicios",
            ...     impacted_components=["UserService", "PaymentService"],
            ...     triggered_by="validator"
            ... )
        """
        # Crear objeto Decision
        decision_obj = Decision(
            iteration=iteration,
            phase=phase,
            timestamp=datetime.now(),
            decision=decision,
            rationale=rationale,
            alternatives_considered=alternatives_considered or [],
            chosen_alternative=chosen_alternative or "",
            impacted_components=impacted_components or [],
            triggered_by=triggered_by or "manual"
        )
        
        # Guardar en storage (append-only)
        self.storage.save_decision(self.project_name, decision_obj)
        
        return decision_obj
    
    def get_all_decisions(self) -> List[Decision]:
        """
        Obtiene todas las decisiones del proyecto, ordenadas cronológicamente.
        
        Returns:
            List[Decision]: Lista de todas las decisiones registradas
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> decisions = logger.get_all_decisions()
            >>> for d in decisions:
            ...     print(f"[Iter {d.iteration}] {d.decision}")
        """
        decisions = self.storage.get_decisions(self.project_name)
        
        # Ordenar por timestamp (más antiguas primero)
        return sorted(decisions, key=lambda d: d.timestamp)
    
    def get_decisions_for_iteration(self, iteration: int) -> List[Decision]:
        """
        Obtiene todas las decisiones de una iteración específica.
        
        Args:
            iteration: Número de iteración
        
        Returns:
            List[Decision]: Decisiones de la iteración especificada
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> decisions_v2 = logger.get_decisions_for_iteration(2)
            >>> print(f"Decisiones en iteración 2: {len(decisions_v2)}")
        """
        all_decisions = self.get_all_decisions()
        return [d for d in all_decisions if d.iteration == iteration]
    
    def get_decisions_for_phase(self, phase: str) -> List[Decision]:
        """
        Obtiene todas las decisiones de una fase específica.
        
        Args:
            phase: Nombre de la fase (analyzer, codegen, validator)
        
        Returns:
            List[Decision]: Decisiones de la fase especificada
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> analyzer_decisions = logger.get_decisions_for_phase("analyzer")
        """
        all_decisions = self.get_all_decisions()
        return [d for d in all_decisions if d.phase == phase]
    
    def search_decisions(self, query: str) -> List[Decision]:
        """
        Busca decisiones que contengan el texto especificado.
        
        Búsqueda case-insensitive en los campos:
        - decision
        - rationale
        - alternatives_considered
        - chosen_alternative
        
        Args:
            query: Texto a buscar
        
        Returns:
            List[Decision]: Decisiones que contienen el texto buscado
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> results = logger.search_decisions("microservicio")
            >>> for d in results:
            ...     print(f"{d.decision}: {d.rationale}")
        """
        query_lower = query.lower()
        all_decisions = self.get_all_decisions()
        
        results = []
        for decision in all_decisions:
            # Buscar en decision
            if query_lower in decision.decision.lower():
                results.append(decision)
                continue
            
            # Buscar en rationale
            if query_lower in decision.rationale.lower():
                results.append(decision)
                continue
            
            # Buscar en alternatives_considered
            for alt in decision.alternatives_considered:
                if query_lower in alt.lower():
                    results.append(decision)
                    break
            else:
                # Buscar en chosen_alternative
                if decision.chosen_alternative and query_lower in decision.chosen_alternative.lower():
                    results.append(decision)
        
        return results
    
    def get_decision_count(self) -> int:
        """
        Obtiene el número total de decisiones registradas.
        
        Returns:
            int: Cantidad de decisiones
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> count = logger.get_decision_count()
            >>> print(f"Total decisiones: {count}")
        """
        return len(self.get_all_decisions())
    
    def get_decision_summary(self) -> dict:
        """
        Obtiene un resumen estadístico de las decisiones.
        
        Returns:
            dict: Resumen con conteos por iteración y fase
        
        Example:
            >>> logger = DecisionLogger("ecommerce")
            >>> summary = logger.get_decision_summary()
            >>> print(summary)
            {
                'total': 15,
                'by_iteration': {1: 5, 2: 7, 3: 3},
                'by_phase': {'analyzer': 6, 'codegen': 5, 'validator': 4},
                'by_trigger': {'validator': 8, 'user_feedback': 5, 'manual': 2}
            }
        """
        decisions = self.get_all_decisions()
        
        by_iteration = {}
        by_phase = {}
        by_trigger = {}
        
        for decision in decisions:
            # Por iteración
            by_iteration[decision.iteration] = by_iteration.get(decision.iteration, 0) + 1
            
            # Por fase
            by_phase[decision.phase] = by_phase.get(decision.phase, 0) + 1
            
            # Por trigger
            trigger = decision.triggered_by or "manual"
            by_trigger[trigger] = by_trigger.get(trigger, 0) + 1
        
        return {
            'total': len(decisions),
            'by_iteration': by_iteration,
            'by_phase': by_phase,
            'by_trigger': by_trigger
        }
        
