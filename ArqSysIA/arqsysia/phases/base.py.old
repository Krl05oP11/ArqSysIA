"""
Clase base para todas las fases del pipeline.

Proporciona funcionalidad común: logging, timing, manejo de errores.
"""

import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from ..clients import OllamaClient, OllamaClientError
from ..core import PhaseResult


class BasePhase(ABC):
    """
    Clase base abstracta para fases del pipeline.
    
    Todas las fases (Analyzer, CodeGen, Validator) heredan de esta clase
    y deben implementar el método execute().
    """
    
    def __init__(
        self,
        client: OllamaClient,
        model: str,
        phase_name: str,
        verbose: bool = True
    ):
        """
        Inicializa la fase.
        
        Args:
            client: Cliente Ollama configurado
            model: Nombre del modelo a usar
            phase_name: Nombre de la fase (para logging)
            verbose: Si True, imprime información de progreso
        """
        self.client = client
        self.model = model
        self.phase_name = phase_name
        self.verbose = verbose
        
        # Verificar que el modelo esté disponible
        if not self.client.check_model_available(model):
            raise ValueError(
                f"Modelo '{model}' no está disponible. "
                f"Descárgalo con: ollama pull {model}"
            )
    
    def log(self, message: str, level: str = "INFO"):
        """Imprime mensaje si verbose está activado."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "WARNING": "⚠️",
                "PROGRESS": "⏳"
            }.get(level, "•")
            print(f"[{timestamp}] {prefix} {message}")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la fase.
        
        Debe ser implementado por cada fase específica.
        
        Returns:
            Diccionario con los resultados de la fase
        """
        pass
    
    def run(self, *args, **kwargs) -> PhaseResult:
        """
        Ejecuta la fase con timing y manejo de errores.
        
        Wrapper alrededor de execute() que agrega:
        - Medición de tiempo
        - Manejo de errores
        - Logging automático
        - Retorno de PhaseResult
        
        Returns:
            PhaseResult con información de ejecución
        """
        self.log(f"Iniciando fase: {self.phase_name}", "PROGRESS")
        start_time = time.time()
        started_at = datetime.now().isoformat()
        
        try:
            # Ejecutar la fase
            output = self.execute(*args, **kwargs)
            
            # Calcular duración
            duration = time.time() - start_time
            completed_at = datetime.now().isoformat()
            
            self.log(
                f"Fase '{self.phase_name}' completada en {duration:.2f}s",
                "SUCCESS"
            )
            
            return PhaseResult(
                phase=self.phase_name,
                status="completed",
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                model_used=self.model,
                output=output
            )
            
        except Exception as e:
            duration = time.time() - start_time
            completed_at = datetime.now().isoformat()
            
            error_msg = f"Error en fase '{self.phase_name}': {str(e)}"
            self.log(error_msg, "ERROR")
            
            return PhaseResult(
                phase=self.phase_name,
                status="failed",
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                model_used=self.model,
                error=error_msg
            )
    
    def generate_with_retry(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2
    ) -> str:
        """
        Genera respuesta con reintentos automáticos.
        
        Args:
            prompt: Prompt del usuario
            system: Prompt del sistema
            temperature: Temperatura de generación
            max_retries: Número máximo de reintentos
            
        Returns:
            Respuesta del modelo
            
        Raises:
            OllamaClientError: Si falla después de reintentos
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.log(f"Reintento {attempt}/{max_retries}...", "WARNING")
                
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    system=system,
                    temperature=temperature
                )
                
                return response
                
            except OllamaClientError as e:
                if attempt == max_retries:
                    raise
                self.log(f"Intento fallido: {str(e)}", "WARNING")
                time.sleep(2)  # Espera antes de reintentar
        
        raise OllamaClientError("No se pudo generar respuesta después de reintentos")
        
