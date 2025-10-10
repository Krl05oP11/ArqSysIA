"""
Fase 1: Analyzer - Análisis Arquitectural

Analiza requerimientos y genera:
- Requerimientos funcionales y no funcionales
- Patrón arquitectural con justificación
- Stack tecnológico
- Componentes principales
- Estructura de directorios
- Dependencias
- MVP scope
- Roadmap del producto
"""

import json
import re
from typing import Dict, Any

from .base import BasePhase
from ..core import AnalysisResult


class AnalyzerPhase(BasePhase):
    """
    Fase 1: Análisis arquitectural de requerimientos.
    
    Usa DeepSeek-R1 para realizar análisis profundo y generar
    propuesta arquitectural completa.
    """
    
    def __init__(self, client, model: str = "deepseek-r1:32b", verbose: bool = True):
        """
        Inicializa el Analyzer.
        
        Args:
            client: Cliente Ollama
            model: Modelo a usar (default: deepseek-r1:32b)
            verbose: Mostrar progreso
        """
        super().__init__(client, model, "analyzer", verbose)
    
    def execute(self, requirements: str) -> Dict[str, Any]:
        """
        Ejecuta el análisis arquitectural.
        
        Args:
            requirements: Requerimientos del sistema en texto libre
            
        Returns:
            Dict con análisis completo (convertible a AnalysisResult)
        """
        self.log("Analizando requerimientos...", "PROGRESS")
        
        # Generar análisis con el modelo
        analysis_text = self._generate_analysis(requirements)
        
        self.log("Parseando resultados...", "PROGRESS")
        
        # Parsear respuesta a estructura
        analysis_dict = self._parse_analysis(analysis_text)
        
        self.log(
            f"Análisis completado: {len(analysis_dict.get('functional_requirements', []))} "
            f"req. funcionales, stack: {analysis_dict.get('architecture_pattern', 'N/A')}",
            "SUCCESS"
        )
        
        return analysis_dict
    
    def _generate_analysis(self, requirements: str) -> str:
        """Genera análisis usando el modelo."""
        
        system_prompt = """Eres un arquitecto de software senior experto en diseño de sistemas.
Tu tarea es analizar requerimientos y proponer arquitecturas de software robustas y bien justificadas.

IMPORTANTE:
- Prioriza tecnologías open-source
- Justifica todas tus decisiones arquitecturales
- Considera escalabilidad, mantenibilidad y seguridad
- Sé específico en las recomendaciones
- Genera respuestas en formato JSON válido"""

        user_prompt = f"""Analiza los siguientes requerimientos y genera una propuesta arquitectural completa:

REQUERIMIENTOS:
{requirements}

Genera tu análisis en el siguiente formato JSON (sin markdown, solo JSON puro):

{{
  "functional_requirements": [
    "Requerimiento funcional 1",
    "Requerimiento funcional 2",
    ...
  ],
  "non_functional_requirements": [
    "Requerimiento no funcional 1 (rendimiento, seguridad, etc.)",
    "Requerimiento no funcional 2",
    ...
  ],
  "architecture_pattern": "Nombre del patrón arquitectural",
  "architecture_justification": "Explicación detallada de por qué elegiste este patrón",
  "tech_stack": {{
    "backend": "Framework/tecnología de backend",
    "database": "Sistema de base de datos",
    "frontend": "Framework frontend (si aplica)",
    "otros": "Otras tecnologías necesarias"
  }},
  "main_components": [
    "Componente principal 1",
    "Componente principal 2",
    ...
  ],
  "directory_structure": "Estructura de directorios propuesta (texto plano)",
  "dependencies": {{
    "backend": ["dependencia1", "dependencia2"],
    "frontend": ["dependencia1", "dependencia2"],
    "devops": ["herramienta1", "herramienta2"]
  }},
  "mvp_scope": "Descripción del alcance del MVP - qué incluir en la primera versión",
  "product_roadmap": "Roadmap del producto completo - fases después del MVP"
}}

RECUERDA: Responde SOLO con el JSON, sin explicaciones adicionales antes o después."""

        response = self.generate_with_retry(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.3  # Baja temperatura para respuestas más consistentes
        )
        
        return response
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del modelo a diccionario.
        
        Maneja:
        - JSON puro
        - JSON dentro de bloques <think>...</think>
        - JSON dentro de markdown ```json...```
        """
        # Remover bloques <think>...</think> de DeepSeek-R1
        cleaned = re.sub(r'<think>.*?</think>', '', analysis_text, flags=re.DOTALL)
        
        # Remover bloques de markdown ```json...```
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # Limpiar espacios
        cleaned = cleaned.strip()
        
        try:
            # Intentar parsear como JSON
            analysis_dict = json.loads(cleaned)
            
            # Validar estructura mínima
            required_keys = [
                'functional_requirements',
                'architecture_pattern',
                'tech_stack'
            ]
            
            for key in required_keys:
                if key not in analysis_dict:
                    self.log(f"Advertencia: Falta clave '{key}' en análisis", "WARNING")
            
            return analysis_dict
            
        except json.JSONDecodeError as e:
            self.log(f"Error parseando JSON: {e}", "ERROR")
            self.log(f"Texto recibido: {cleaned[:500]}...", "ERROR")
            
            # Retornar estructura mínima en caso de error
            return {
                "functional_requirements": ["Error: No se pudo parsear respuesta"],
                "non_functional_requirements": [],
                "architecture_pattern": "Error",
                "architecture_justification": "No se pudo generar análisis",
                "tech_stack": {},
                "main_components": [],
                "directory_structure": "",
                "dependencies": {},
                "mvp_scope": "",
                "product_roadmap": "",
                "_raw_response": cleaned
            }
    
    def to_analysis_result(self, analysis_dict: Dict[str, Any]) -> AnalysisResult:
        """
        Convierte diccionario a AnalysisResult.
        
        Args:
            analysis_dict: Diccionario con análisis
            
        Returns:
            AnalysisResult estructurado
        """
        return AnalysisResult(
            functional_requirements=analysis_dict.get('functional_requirements', []),
            non_functional_requirements=analysis_dict.get('non_functional_requirements', []),
            architecture_pattern=analysis_dict.get('architecture_pattern'),
            architecture_justification=analysis_dict.get('architecture_justification'),
            tech_stack=analysis_dict.get('tech_stack', {}),
            main_components=analysis_dict.get('main_components', []),
            directory_structure=analysis_dict.get('directory_structure'),
            dependencies=analysis_dict.get('dependencies', {}),
            mvp_scope=analysis_dict.get('mvp_scope'),
            product_roadmap=analysis_dict.get('product_roadmap')
        )


# Función helper para crear analyzer fácilmente
def create_analyzer(client, model: str = "deepseek-r1:32b", verbose: bool = True) -> AnalyzerPhase:
    """
    Crea una instancia de AnalyzerPhase.
    
    Args:
        client: Cliente Ollama
        model: Modelo a usar
        verbose: Mostrar progreso
        
    Returns:
        AnalyzerPhase configurado
    """
    return AnalyzerPhase(client, model, verbose)
    
