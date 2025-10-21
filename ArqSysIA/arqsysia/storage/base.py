"""
StorageBackend - Interfaz abstracta para backends de almacenamiento
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class StorageBackend(ABC):
    """Interfaz abstracta para backends de almacenamiento"""
    
    @abstractmethod
    def save_iteration(self, iteration) -> None:
        """Guarda una iteración completa"""
        pass
    
    @abstractmethod
    def load_iteration(self, project_name: str, iteration_number: int):
        """Carga una iteración específica"""
        pass
    
    @abstractmethod
    def list_iterations(self, project_name: str) -> List:
        """Lista todas las iteraciones de un proyecto"""
        pass
    
    @abstractmethod
    def save_decision(self, project_name: str, decision) -> None:
        """Guarda una decisión"""
        pass
    
    @abstractmethod
    def get_decisions(
        self, 
        project_name: str, 
        iteration: Optional[int] = None
    ) -> List:
        """Obtiene decisiones (todas o de una iteración específica)"""
        pass
    
    @abstractmethod
    def save_metadata(self, metadata) -> None:
        """Guarda metadata del proyecto"""
        pass
    
    @abstractmethod
    def load_metadata(self, project_name: str):
        """Carga metadata del proyecto"""
        pass
    
    @abstractmethod
    def delete_iteration(self, project_name: str, iteration_number: int) -> None:
        """Elimina una iteración (para rollback)"""
        pass
