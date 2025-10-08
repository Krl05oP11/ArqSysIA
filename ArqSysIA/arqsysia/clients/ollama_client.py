"""
Cliente para interactuar con Ollama API.

Proporciona interfaz simple y robusta para llamadas a modelos LLM
con retry logic, manejo de errores y streaming opcional.
"""

import json
import time
from typing import Optional, Dict, Any, Generator
from dataclasses import dataclass

try:
    import ollama
except ImportError:
    raise ImportError(
        "El paquete 'ollama' no está instalado. "
        "Instálalo con: pip install ollama"
    )


@dataclass
class OllamaConfig:
    """Configuración del cliente Ollama."""
    host: str = "http://localhost:11434"
    timeout: int = 300  # 5 minutos
    max_retries: int = 3
    retry_delay: int = 2  # segundos


class OllamaClient:
    """
    Cliente para Ollama API con retry logic y manejo de errores.
    
    Ejemplo de uso:
        client = OllamaClient()
        response = client.generate(
            model="deepseek-r1:32b",
            prompt="Analiza esta arquitectura...",
            system="Eres un arquitecto de software experto."
        )
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        Inicializa el cliente Ollama.
        
        Args:
            config: Configuración del cliente. Si es None, usa valores por defecto.
        """
        self.config = config or OllamaConfig()
        self.client = ollama.Client(host=self.config.host)
        
    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> str | Generator[str, None, None]:
        """
        Genera respuesta del modelo.
        
        Args:
            model: Nombre del modelo (ej: "deepseek-r1:32b")
            prompt: Prompt del usuario
            system: Prompt del sistema (opcional)
            temperature: Temperatura de generación (0.0 a 1.0)
            stream: Si True, retorna generator para streaming
            **kwargs: Parámetros adicionales para Ollama
            
        Returns:
            str: Respuesta completa del modelo (si stream=False)
            Generator: Generator de chunks (si stream=True)
            
        Raises:
            OllamaClientError: Si falla después de reintentos
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": temperature,
            **kwargs
        }
        
        for attempt in range(self.config.max_retries):
            try:
                if stream:
                    return self._stream_generate(model, messages, options)
                else:
                    return self._blocking_generate(model, messages, options)
                    
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise OllamaClientError(
                        f"Fallo después de {self.config.max_retries} intentos: {str(e)}"
                    ) from e
                
                print(f"⚠️  Intento {attempt + 1} falló: {str(e)}")
                print(f"   Reintentando en {self.config.retry_delay}s...")
                time.sleep(self.config.retry_delay)
    
    def _blocking_generate(
        self,
        model: str,
        messages: list,
        options: dict
    ) -> str:
        """Generación bloqueante (espera respuesta completa)."""
        response = self.client.chat(
            model=model,
            messages=messages,
            options=options
        )
        
        if not response or 'message' not in response:
            raise OllamaClientError("Respuesta inválida de Ollama")
        
        return response['message']['content']
    
    def _stream_generate(
        self,
        model: str,
        messages: list,
        options: dict
    ) -> Generator[str, None, None]:
        """Generación con streaming (chunks progresivos)."""
        stream = self.client.chat(
            model=model,
            messages=messages,
            options=options,
            stream=True
        )
        
        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    
    def list_models(self) -> list[str]:
        """
        Lista modelos disponibles en Ollama.
        
        Returns:
            Lista de nombres de modelos
        """
        try:
            response = self.client.list()
            # response es un objeto ListResponse, accedemos a models como atributo
            models = response.models if hasattr(response, 'models') else response.get('models', [])
            
            # Los modelos son objetos con atributo 'model' que contiene el nombre
            result = []
            for model in models:
                if isinstance(model, dict):
                    name = model.get('name') or model.get('model', 'unknown')
                else:
                    # Es un objeto, el nombre está en el atributo 'model'
                    name = str(model.model) if hasattr(model, 'model') else str(model)
                
                result.append(name)
            
            return result
        except Exception as e:
            raise OllamaClientError(f"Error listando modelos: {str(e)}") from e
    
    def check_model_available(self, model: str) -> bool:
        """
        Verifica si un modelo está disponible.
        
        Args:
            model: Nombre del modelo
            
        Returns:
            True si el modelo está disponible
        """
        try:
            available_models = self.list_models()
            return model in available_models
        except Exception:
            return False
    
    def ping(self) -> bool:
        """
        Verifica conectividad con Ollama.
        
        Returns:
            True si Ollama está accesible
        """
        try:
            self.list_models()
            return True
        except Exception:
            return False


class OllamaClientError(Exception):
    """Excepción para errores del cliente Ollama."""
    pass


# Función helper para crear cliente con configuración simple
def create_client(host: str = "http://localhost:11434") -> OllamaClient:
    """
    Crea cliente Ollama con configuración básica.
    
    Args:
        host: URL del servidor Ollama
        
    Returns:
        Cliente Ollama configurado
    """
    config = OllamaConfig(host=host)
    return OllamaClient(config)
