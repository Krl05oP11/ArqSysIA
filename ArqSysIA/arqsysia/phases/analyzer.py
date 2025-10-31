"""
Analyzer Phase - Fase 1 del Pipeline ArqSysIA

Analiza requerimientos y genera propuesta arquitectural completa.
"""

import json
import re
from typing import Dict, Any

from arqsysia.phases.base import BasePhase
from arqsysia.core.state import ProjectState
from arqsysia.clients.ollama_client import OllamaClient


class AnalyzerPhase(BasePhase):
    """
    Fase 1: Análisis Arquitectural
    
    Analiza los requerimientos del proyecto y genera:
    - Requerimientos funcionales y no funcionales
    - Patrón arquitectural justificado
    - Stack tecnológico
    - Componentes principales
    - Estructura de directorios
    - Dependencias
    - Alcance del MVP
    - Roadmap completo del producto
    """
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        model_name: str = "deepseek-r1:32b"
    ):
        """
        Inicializa la fase de análisis.
        
        Args:
            ollama_client: Cliente para interactuar con Ollama
            model_name: Nombre del modelo LLM a usar
        """
        super().__init__(
            name="Analyzer",
            ollama_client=ollama_client,
            model_name=model_name
        )
    
    def run(self, state: ProjectState) -> ProjectState:
        """
        Ejecuta el análisis arquitectural.
        
        Args:
            state: Estado del proyecto con requerimientos
            
        Returns:
            Estado actualizado con análisis completo
        """
        self.log("Iniciando análisis arquitectural...")
        
        # Construir prompt
        prompt = self._build_analysis_prompt(state)
        
        # Llamar al modelo
        self.log("Consultando a DeepSeek-R1 (esto puede tomar 4-5 minutos)...")
        response = self.ollama_client.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 4096,
            }
        )
        
        # Parsear respuesta
        self.log("Parseando análisis...")
        analysis = self._parse_analysis_response(response)
        
        # Guardar en el estado
        state.outputs["analysis"]["analysis"] = analysis
        
        
        self.log("✅ Análisis completado exitosamente")
        return state
    
    def _build_analysis_prompt(self, state: ProjectState) -> str:
        """Construye el prompt para el análisis arquitectural."""
        
        prompt = f"""Eres un arquitecto de software senior experto. Analiza los siguientes requerimientos y genera una propuesta arquitectural completa y profesional.

## Requerimientos del Proyecto

**Nombre del Proyecto:** {state.project_name}

**Descripción y Requerimientos:**
{state.original_requirements}

## Tu Tarea

Realiza un análisis arquitectural COMPLETO y genera un documento estructurado en formato JSON con la siguiente información:

1. **Requerimientos Funcionales**: Lista de funcionalidades específicas que el sistema debe proporcionar
2. **Requerimientos No Funcionales**: Restricciones, atributos de calidad (performance, seguridad, escalabilidad, etc.)
3. **Patrón Arquitectural**: Propón UN patrón arquitectural apropiado (ej: Monolito MVC, Microservicios, Serverless, etc.)
4. **Justificación Arquitectural**: Explica por qué elegiste ese patrón considerando el contexto del proyecto
5. **Stack Tecnológico**: Propón tecnologías específicas para cada capa (frontend, backend, base de datos, etc.)
6. **Componentes Principales**: Lista los componentes/módulos principales del sistema con sus responsabilidades
7. **Estructura de Directorios**: Propón la estructura básica de archivos y carpetas
8. **Dependencias**: Lista las dependencias técnicas principales (librerías, frameworks, servicios)
9. **Alcance del MVP**: Define qué funcionalidades incluir en el MVP (Producto Mínimo Viable)
10. **Roadmap del Producto**: Propón fases de desarrollo desde MVP hasta producto completo

## IMPORTANTE - Considera el Contexto

- Si el proyecto es para un **desarrollador individual**, prioriza **SIMPLICIDAD** sobre complejidad
- Para proyectos pequeños/medianos de un solo desarrollador, un **monolito bien estructurado** suele ser mejor que microservicios
- Solo sugiere arquitecturas complejas (microservicios, event-driven, etc.) si están **justificadas** por requisitos específicos de escala o complejidad
- Prioriza tecnologías **open-source, maduras y bien documentadas**

## Formato de Respuesta

Responde ÚNICAMENTE con un objeto JSON válido, SIN bloques de código markdown, con esta estructura:

{{
  "functional_requirements": ["req1", "req2", ...],
  "non_functional_requirements": ["req1", "req2", ...],
  "architecture_pattern": "Nombre del patrón",
  "architecture_justification": "Explicación detallada de por qué este patrón es apropiado...",
  "tech_stack": {{
    "frontend": "tecnología",
    "backend": "tecnología",
    "database": "tecnología",
    "otros": "..."
  }},
  "main_components": [
    {{
      "name": "Nombre del componente",
      "description": "Descripción",
      "responsibilities": ["resp1", "resp2"]
    }}
  ],
  "directory_structure": {{
    "descripción": "de la estructura básica"
  }},
  "dependencies": {{
    "frontend": ["dep1", "dep2"],
    "backend": ["dep1", "dep2"],
    "devops": ["dep1", "dep2"]
  }},
  "mvp_scope": ["feature1", "feature2", ...],
  "roadmap": [
    {{
      "phase": "MVP",
      "duration": "X semanas/meses",
      "description": "...",
      "features": ["f1", "f2"]
    }}
  ]
}}

**CRÍTICO**: 
- NO uses bloques markdown (```json)
- NO incluyas texto fuera del JSON
- El JSON debe ser válido y parseable
- Sé específico y práctico en tus recomendaciones

Genera el análisis ahora:"""
        
        return prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del modelo y extrae el análisis estructurado.
        
        Args:
            response: Respuesta cruda del modelo
            
        Returns:
            Diccionario con el análisis estructurado
        """
        try:
            # Limpiar la respuesta
            cleaned = self._clean_response(response)
            
            # Intentar parsear JSON
            analysis = json.loads(cleaned)
            
            # Validar estructura mínima
            required_keys = [
                "functional_requirements",
                "non_functional_requirements",
                "architecture_pattern",
                "tech_stack"
            ]
            
            for key in required_keys:
                if key not in analysis:
                    self.log(f"⚠️  Advertencia: falta clave '{key}' en el análisis")
            
            return analysis
            
        except json.JSONDecodeError as e:
            self.log(f"❌ Error parseando JSON: {e}")
            self.log(f"Respuesta recibida (primeros 500 chars): {response[:500]}")
            
            # Retornar análisis mínimo en caso de error
            return {
                "functional_requirements": ["Error parseando respuesta"],
                "non_functional_requirements": [],
                "architecture_pattern": "No disponible",
                "tech_stack": {},
                "main_components": [],
                "mvp_scope": [],
                "roadmap": [],
                "error": str(e),
                "raw_response": response[:1000]
            }
    
    def _clean_response(self, response: str) -> str:
        """
        Limpia la respuesta del modelo removiendo bloques <think>, markdown, etc.
        
        Args:
            response: Respuesta cruda del modelo
            
        Returns:
            Respuesta limpia
        """
        # Remover bloques <think>...</think>
        cleaned = re.sub(
            r'<think>.*?</think>',
            '',
            response,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Remover bloques de código markdown
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # Remover espacios al inicio y final
        cleaned = cleaned.strip()
        
        return cleaned
