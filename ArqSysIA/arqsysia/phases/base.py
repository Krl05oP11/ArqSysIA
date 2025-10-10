"""
Clase base para todas las fases del pipeline.

Proporciona funcionalidad común: logging, validación, manejo de errores.
"""

from typing import Any
from arqsysia.clients.ollama_client import OllamaClient
from arqsysia.core.state import ProjectState


class BasePhase:
    """
    Clase base para todas las fases del pipeline.
    
    Proporciona funcionalidad común como logging y validación.
    Todas las fases (Analyzer, CodeGen, Validator) heredan de esta clase.
    """
    
    def __init__(
        self,
        name: str,
        ollama_client: OllamaClient,
        model_name: str
    ):
        """
        Inicializa la fase.
        
        Args:
            name: Nombre de la fase (ej: "Analyzer", "CodeGen", "Validator")
            ollama_client: Cliente para interactuar con Ollama
            model_name: Nombre del modelo LLM a usar
        """
        self.name = name
        self.ollama_client = ollama_client
        self.model_name = model_name
    
    def run(self, state: ProjectState) -> ProjectState:
        """
        Ejecuta la fase. Debe ser implementado por las subclases.
        
        Args:
            state: Estado actual del proyecto
            
        Returns:
            Estado actualizado después de ejecutar la fase
        """
        raise NotImplementedError(f"La fase {self.name} debe implementar el método run()")
    
    def log(self, message: str):
        """
        Imprime un mensaje de log con el nombre de la fase.
        
        Args:
            message: Mensaje a imprimir
        """
        print(f"[{self.name}] {message}")
    
    def validate_state(self, state: ProjectState, required_outputs: list = None):
        """
        Valida que el estado tenga los outputs requeridos.
        
        Args:
            state: Estado del proyecto
            required_outputs: Lista de keys que deben existir en outputs
            
        Raises:
            ValueError: Si falta algún output requerido
        """
        if required_outputs:
            for key in required_outputs:
                if key not in state.outputs:
                    raise ValueError(
                        f"El estado no contiene el output requerido: '{key}'"
                    )
                    
