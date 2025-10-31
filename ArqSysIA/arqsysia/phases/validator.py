"""
Validator Phase - Fase 3 del Pipeline ArqSysIA

Valida la arquitectura diseñada y el código generado, identificando:
- Inconsistencias entre componentes
- Errores potenciales
- Mejoras sugeridas
- Consideraciones de seguridad
- Optimizaciones
- Elementos faltantes
"""

import json
import re
from typing import Dict, Any, List
from arqsysia.phases.base import BasePhase
from arqsysia.core.state import ProjectState


class ValidatorPhase(BasePhase):
    """
    Fase 3: Validación de arquitectura y código generado.
    
    Usa DeepSeek-R1:14B para análisis rápido de validación.
    """
    
    def __init__(
        self,
        ollama_client,
        model_name: str = "deepseek-r1:14b"
    ):
        """
        Inicializa la fase de validación.
        
        Args:
            ollama_client: Cliente de Ollama configurado
            model_name: Nombre del modelo a usar (default: deepseek-r1:14b)
        """
        super().__init__(
            name="Validator",
            ollama_client=ollama_client,
            model_name=model_name
        )
    
    def run(self, state: ProjectState) -> ProjectState:
        """
        Ejecuta la validación completa.
        
        Args:
            state: Estado del proyecto con resultados de Analyzer y CodeGen
            
        Returns:
            ProjectState actualizado con resultados de validación
        """
        print(f"\n{'='*60}")
        print(f"🔍 FASE 3: VALIDACIÓN")
        print(f"{'='*60}")
        print(f"Modelo: {self.model_name}")
        print(f"Proyecto: {state.project_name}\n")
        
        # Validar que existan outputs previos (compatible con versiones anteriores)
        has_analysis = (
            state.outputs.get("analysis_complete") or 
            state.outputs.get("analysis") is not None or
            state.outputs.get("architecture_analysis") is not None
        )
        if not has_analysis:
            raise ValueError("Analyzer debe ejecutarse antes del Validator")
        
        # Ejecutar validaciones
        validation_results = {}
        
        # 1. Validar arquitectura
        print("📐 Validando arquitectura...")
        architecture_validation = self._validate_architecture(state)
        validation_results["architecture"] = architecture_validation
        
        # 2. Validar código (si existe) - compatible con versiones anteriores
        has_codegen = (
            state.outputs.get("codegen_complete") or 
            state.outputs.get("file_structure") is not None or
            state.outputs.get("generated_files") is not None
        )
        if has_codegen:
            print("\n💻 Validando código generado...")
            code_validation = self._validate_code(state)
            validation_results["code"] = code_validation
        
        # 3. Análisis de seguridad
        print("\n🔒 Analizando seguridad...")
        security_analysis = self._analyze_security(state)
        validation_results["security"] = security_analysis
        
        # 4. Sugerencias de optimización
        print("\n⚡ Generando optimizaciones...")
        optimizations = self._suggest_optimizations(state)
        validation_results["optimizations"] = optimizations
        
        # Guardar resultados en el estado
        state.outputs["validation"]["validation_results"] = validation_results
        state.outputs["validation"]["validation_complete"] = True
        
        # Generar reporte consolidado
        report = self._generate_report(validation_results)
        state.outputs["validation"]["validation_report"] = report
        
        print(f"\n✅ Validación completada")
        print(f"{'='*60}\n")
        
        return state
    
    def _validate_architecture(self, state: ProjectState) -> Dict[str, Any]:
        """Valida la arquitectura diseñada por el Analyzer."""
        
        # Construir contexto de la arquitectura
        context = self._build_architecture_context(state)
        
        prompt = f"""Eres un arquitecto de software experto. Analiza la siguiente arquitectura y proporciona una validación crítica.

CONTEXTO DEL PROYECTO:
{context}

Tu tarea es identificar:
1. **Inconsistencias**: Conflictos entre componentes, arquitectura y stack tecnológico
2. **Errores de diseño**: Decisiones arquitecturales problemáticas
3. **Componentes faltantes**: Elementos críticos no considerados
4. **Mejoras**: Sugerencias para fortalecer el diseño

IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown, sin bloques de código):

{{
  "inconsistencies": [
    {{
      "severity": "high|medium|low",
      "component": "nombre del componente",
      "description": "descripción del problema",
      "impact": "impacto en el sistema"
    }}
  ],
  "design_errors": [
    {{
      "severity": "high|medium|low",
      "area": "área afectada",
      "description": "descripción del error",
      "recommendation": "cómo corregirlo"
    }}
  ],
  "missing_components": [
    {{
      "component": "nombre del componente faltante",
      "reason": "por qué es necesario",
      "priority": "high|medium|low"
    }}
  ],
  "improvements": [
    {{
      "area": "área a mejorar",
      "suggestion": "sugerencia específica",
      "benefit": "beneficio esperado"
    }}
  ],
  "overall_assessment": "evaluación general de la arquitectura (2-3 líneas)",
  "architecture_score": 0-10
}}"""

        try:
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.3,  # Más determinista para validación
                stream=False
            )
            
            # Limpiar respuesta
            cleaned = self._clean_response(response)
            result = json.loads(cleaned)
            
            # Mostrar resumen
            self._print_architecture_summary(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error en validación de arquitectura: {e}")
            return {
                "error": str(e),
                "inconsistencies": [],
                "design_errors": [],
                "missing_components": [],
                "improvements": [],
                "overall_assessment": "Error al validar arquitectura",
                "architecture_score": 0
            }
    
    def _validate_code(self, state: ProjectState) -> Dict[str, Any]:
        """Valida el código generado por CodeGen."""
        
        # Construir contexto del código generado
        context = self._build_code_context(state)
        
        prompt = f"""Eres un experto en revisión de código. Analiza el código y estructura generados.

CONTEXTO DEL CÓDIGO:
{context}

Tu tarea es identificar:
1. **Errores potenciales**: Bugs, problemas de sintaxis, malas prácticas
2. **Code smells**: Código problemático que funciona pero debería mejorarse
3. **Problemas de estructura**: Organización de archivos y dependencias
4. **Mejoras de calidad**: Sugerencias para código más limpio y mantenible

IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown):

{{
  "potential_errors": [
    {{
      "severity": "high|medium|low",
      "file": "archivo afectado",
      "description": "descripción del error",
      "fix": "cómo corregirlo"
    }}
  ],
  "code_smells": [
    {{
      "file": "archivo afectado",
      "smell": "tipo de code smell",
      "description": "descripción",
      "refactor_suggestion": "sugerencia de refactorización"
    }}
  ],
  "structure_issues": [
    {{
      "area": "área afectada",
      "issue": "descripción del problema",
      "recommendation": "recomendación"
    }}
  ],
  "quality_improvements": [
    {{
      "area": "área a mejorar",
      "suggestion": "sugerencia específica",
      "benefit": "beneficio esperado"
    }}
  ],
  "code_quality_score": 0-10
}}"""

        try:
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.3,
                stream=False
            )
            
            cleaned = self._clean_response(response)
            result = json.loads(cleaned)
            
            # Mostrar resumen
            self._print_code_summary(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error en validación de código: {e}")
            return {
                "error": str(e),
                "potential_errors": [],
                "code_smells": [],
                "structure_issues": [],
                "quality_improvements": [],
                "code_quality_score": 0
            }
    
    def _analyze_security(self, state: ProjectState) -> Dict[str, Any]:
        """Analiza consideraciones de seguridad."""
        
        # Construir contexto de seguridad
        context = self._build_security_context(state)
        
        prompt = f"""Eres un experto en seguridad de aplicaciones. Analiza los aspectos de seguridad del proyecto.

CONTEXTO DEL PROYECTO:
{context}

Tu tarea es identificar:
1. **Vulnerabilidades potenciales**: Problemas de seguridad críticos
2. **Mejores prácticas no implementadas**: Estándares de seguridad faltantes
3. **Riesgos de datos**: Exposición, almacenamiento, transmisión
4. **Recomendaciones**: Mejoras de seguridad prioritarias

IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown):

{{
  "vulnerabilities": [
    {{
      "severity": "critical|high|medium|low",
      "category": "categoría (auth, injection, etc)",
      "description": "descripción de la vulnerabilidad",
      "mitigation": "cómo mitigarla"
    }}
  ],
  "missing_practices": [
    {{
      "practice": "práctica de seguridad faltante",
      "importance": "por qué es importante",
      "implementation": "cómo implementarla"
    }}
  ],
  "data_risks": [
    {{
      "risk_type": "tipo de riesgo",
      "description": "descripción del riesgo",
      "recommendation": "recomendación"
    }}
  ],
  "priority_recommendations": [
    {{
      "priority": 1-5,
      "recommendation": "recomendación específica",
      "impact": "impacto en seguridad"
    }}
  ],
  "security_score": 0-10
}}"""

        try:
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.3,
                stream=False
            )
            
            cleaned = self._clean_response(response)
            result = json.loads(cleaned)
            
            # Mostrar resumen
            self._print_security_summary(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error en análisis de seguridad: {e}")
            return {
                "error": str(e),
                "vulnerabilities": [],
                "missing_practices": [],
                "data_risks": [],
                "priority_recommendations": [],
                "security_score": 0
            }
    
    def _suggest_optimizations(self, state: ProjectState) -> Dict[str, Any]:
        """Sugiere optimizaciones para el proyecto."""
        
        # Construir contexto de optimización
        context = self._build_optimization_context(state)
        
        prompt = f"""Eres un experto en optimización de software. Analiza el proyecto y sugiere optimizaciones.

CONTEXTO DEL PROYECTO:
{context}

Tu tarea es sugerir optimizaciones en:
1. **Performance**: Rendimiento y velocidad
2. **Escalabilidad**: Capacidad de crecimiento
3. **Mantenibilidad**: Facilidad de mantenimiento
4. **Costo**: Reducción de costos operativos

IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown):

{{
  "performance": [
    {{
      "area": "área a optimizar",
      "current_issue": "problema actual",
      "optimization": "optimización sugerida",
      "expected_improvement": "mejora esperada"
    }}
  ],
  "scalability": [
    {{
      "aspect": "aspecto de escalabilidad",
      "suggestion": "sugerencia",
      "benefit": "beneficio"
    }}
  ],
  "maintainability": [
    {{
      "area": "área a mejorar",
      "suggestion": "sugerencia",
      "long_term_benefit": "beneficio a largo plazo"
    }}
  ],
  "cost_reduction": [
    {{
      "area": "área de costo",
      "suggestion": "sugerencia de reducción",
      "estimated_savings": "ahorros estimados"
    }}
  ],
  "priority_optimizations": [
    "lista de optimizaciones prioritarias (strings)"
  ]
}}"""

        try:
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.4,  # Más creatividad para optimizaciones
                stream=False
            )
            
            cleaned = self._clean_response(response)
            result = json.loads(cleaned)
            
            # Mostrar resumen
            self._print_optimization_summary(result)
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error en sugerencias de optimización: {e}")
            return {
                "error": str(e),
                "performance": [],
                "scalability": [],
                "maintainability": [],
                "cost_reduction": [],
                "priority_optimizations": []
            }
    
    def _build_architecture_context(self, state: ProjectState) -> str:
        """Construye contexto de arquitectura para validación."""
        
        context_parts = [
            f"Proyecto: {state.project_name}",
            f"\nRequerimientos originales:",
            state.original_requirements[:800],
        ]
        
        # Intentar obtener análisis de múltiples versiones
        analysis = (
            state.outputs.get("architecture_analysis") or 
            state.outputs.get("analysis") or 
            {}
        )
        
        if analysis:
            # Patrón arquitectural
            pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
            context_parts.append(f"\nPatrón arquitectural: {pattern}")
            
            justification = analysis.get('justification') or analysis.get('architecture_justification', '')
            if justification:
                context_parts.append(f"Justificación: {justification[:300]}")
            
            # Stack tecnológico
            stack = analysis.get('technology_stack') or analysis.get('tech_stack', {})
            if stack:
                context_parts.append(f"\nStack tecnológico:")
                for category, tech in list(stack.items())[:5]:
                    if isinstance(tech, list):
                        context_parts.append(f"  {category}: {', '.join(tech[:3])}")
                    else:
                        context_parts.append(f"  {category}: {tech}")
            
            # Componentes
            components = analysis.get('main_components') or analysis.get('components', [])
            if components:
                context_parts.append(f"\nComponentes principales ({len(components)}):")
                for comp in components[:5]:
                    if isinstance(comp, dict):
                        comp_name = comp.get('name') or comp.get('component', 'N/A')
                        context_parts.append(f"  - {comp_name}")
                    elif isinstance(comp, str):
                        context_parts.append(f"  - {comp}")
        
        return "\n".join(context_parts)
    
    def _build_code_context(self, state: ProjectState) -> str:
        """Construye contexto de código para validación."""
        
        context_parts = [
            f"Proyecto: {state.project_name}",
        ]
        
        # Estructura de archivos
        file_structure = state.outputs.get("file_structure")
        if file_structure:
            if isinstance(file_structure, dict):
                context_parts.append(f"\nEstructura de archivos generada")
            elif isinstance(file_structure, list):
                context_parts.append(f"\nEstructura de archivos: {len(file_structure)} nodos")
        
        # Archivos generados - CORREGIDO: manejar como dict
        generated_files = state.outputs.get("generated_files")
        if generated_files:
            if isinstance(generated_files, dict):
                context_parts.append(f"\nArchivos clave generados: {len(generated_files)}")
                # Tomar primeros 3 archivos
                for filename in list(generated_files.keys())[:3]:
                    context_parts.append(f"  - {filename}")
            elif isinstance(generated_files, list):
                # Fallback para formato antiguo (lista)
                context_parts.append(f"\nArchivos clave generados: {len(generated_files)}")
                for file_info in generated_files[:3]:
                    if isinstance(file_info, dict):
                        filename = file_info.get('filename') or file_info.get('name', 'N/A')
                        context_parts.append(f"  - {filename}")
        
        # Fallback a key_files si existe
        if not generated_files:
            key_files = state.outputs.get("key_files")
            if key_files and isinstance(key_files, list):
                context_parts.append(f"\nArchivos clave: {len(key_files)}")
                for file_info in key_files[:3]:
                    if isinstance(file_info, dict):
                        filename = file_info.get('filename') or file_info.get('name', 'N/A')
                        context_parts.append(f"  - {filename}")
        
        # Scripts
        setup_scripts = state.outputs.get("setup_scripts")
        if setup_scripts:
            if isinstance(setup_scripts, dict):
                context_parts.append(f"\nScripts de setup: {len(setup_scripts)}")
            elif isinstance(setup_scripts, list):
                context_parts.append(f"\nScripts de setup: {len(setup_scripts)}")
        
        return "\n".join(context_parts)
    
    def _build_security_context(self, state: ProjectState) -> str:
        """Construye contexto de seguridad."""
        
        context_parts = [
            f"Proyecto: {state.project_name}",
        ]
        
        # Análisis (compatible con versiones)
        analysis = (
            state.outputs.get("architecture_analysis") or 
            state.outputs.get("analysis") or 
            {}
        )
        
        # Stack tecnológico
        stack = analysis.get('technology_stack') or analysis.get('tech_stack', {})
        if stack:
            context_parts.append("\nStack tecnológico:")
            for category, tech in list(stack.items())[:5]:
                if isinstance(tech, list):
                    context_parts.append(f"  {category}: {', '.join(tech[:3])}")
                else:
                    context_parts.append(f"  {category}: {tech}")
        
        # Tipo de arquitectura
        pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
        context_parts.append(f"\nPatrón arquitectural: {pattern}")
        
        # Requerimientos no funcionales
        non_functional = analysis.get('non_functional_requirements', [])
        if non_functional:
            security_reqs = [
                req for req in non_functional 
                if isinstance(req, str) and ('seguridad' in req.lower() or 'security' in req.lower())
            ]
            if security_reqs:
                context_parts.append(f"\nRequerimientos de seguridad: {len(security_reqs)}")
        
        return "\n".join(context_parts)
    
    def _build_optimization_context(self, state: ProjectState) -> str:
        """Construye contexto de optimización."""
        
        context_parts = [
            f"Proyecto: {state.project_name}",
        ]
        
        # Análisis (compatible con versiones)
        analysis = (
            state.outputs.get("architecture_analysis") or 
            state.outputs.get("analysis") or 
            {}
        )
        
        # Patrón arquitectural
        pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
        context_parts.append(f"\nPatrón arquitectural: {pattern}")
        
        # Stack
        stack = analysis.get('technology_stack') or analysis.get('tech_stack', {})
        if stack:
            context_parts.append("\nStack principal:")
            for category, tech in list(stack.items())[:4]:
                if isinstance(tech, list):
                    context_parts.append(f"  {category}: {', '.join(tech[:3])}")
                else:
                    context_parts.append(f"  {category}: {tech}")
        
        # Componentes
        components = analysis.get('main_components') or analysis.get('components', [])
        if components:
            context_parts.append(f"\nComponentes: {len(components)}")
        
        return "\n".join(context_parts)
    
    def _clean_response(self, response: str) -> str:
        """Limpia la respuesta del LLM para extraer JSON."""
        
        # Remover bloques <think>
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remover markdown
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # Buscar JSON
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        
        return cleaned.strip()
    
    def _print_architecture_summary(self, result: Dict[str, Any]) -> None:
        """Imprime resumen de validación de arquitectura."""
        
        inconsistencies = len(result.get("inconsistencies", []))
        errors = len(result.get("design_errors", []))
        missing = len(result.get("missing_components", []))
        improvements = len(result.get("improvements", []))
        score = result.get("architecture_score", 0)
        
        print(f"   Inconsistencias: {inconsistencies}")
        print(f"   Errores de diseño: {errors}")
        print(f"   Componentes faltantes: {missing}")
        print(f"   Mejoras sugeridas: {improvements}")
        print(f"   📊 Score arquitectura: {score}/10")
    
    def _print_code_summary(self, result: Dict[str, Any]) -> None:
        """Imprime resumen de validación de código."""
        
        errors = len(result.get("potential_errors", []))
        smells = len(result.get("code_smells", []))
        structure = len(result.get("structure_issues", []))
        improvements = len(result.get("quality_improvements", []))
        score = result.get("code_quality_score", 0)
        
        print(f"   Errores potenciales: {errors}")
        print(f"   Code smells: {smells}")
        print(f"   Problemas de estructura: {structure}")
        print(f"   Mejoras de calidad: {improvements}")
        print(f"   📊 Score calidad código: {score}/10")
    
    def _print_security_summary(self, result: Dict[str, Any]) -> None:
        """Imprime resumen de análisis de seguridad."""
        
        vulnerabilities = len(result.get("vulnerabilities", []))
        missing = len(result.get("missing_practices", []))
        risks = len(result.get("data_risks", []))
        recommendations = len(result.get("priority_recommendations", []))
        score = result.get("security_score", 0)
        
        print(f"   Vulnerabilidades: {vulnerabilities}")
        print(f"   Prácticas faltantes: {missing}")
        print(f"   Riesgos de datos: {risks}")
        print(f"   Recomendaciones prioritarias: {recommendations}")
        print(f"   📊 Score seguridad: {score}/10")
    
    def _print_optimization_summary(self, result: Dict[str, Any]) -> None:
        """Imprime resumen de optimizaciones."""
        
        performance = len(result.get("performance", []))
        scalability = len(result.get("scalability", []))
        maintainability = len(result.get("maintainability", []))
        cost = len(result.get("cost_reduction", []))
        priority = len(result.get("priority_optimizations", []))
        
        print(f"   Performance: {performance}")
        print(f"   Escalabilidad: {scalability}")
        print(f"   Mantenibilidad: {maintainability}")
        print(f"   Reducción de costos: {cost}")
        print(f"   📌 Optimizaciones prioritarias: {priority}")
    
    def _generate_report(self, validation_results: Dict[str, Any]) -> str:
        """Genera reporte consolidado de validación."""
        
        report_lines = [
            "# REPORTE DE VALIDACIÓN",
            "=" * 60,
            ""
        ]
        
        # Arquitectura
        if "architecture" in validation_results:
            arch = validation_results["architecture"]
            report_lines.append("## 1. VALIDACIÓN DE ARQUITECTURA")
            report_lines.append(f"Score: {arch.get('architecture_score', 0)}/10")
            report_lines.append(f"Evaluación: {arch.get('overall_assessment', 'N/A')}")
            report_lines.append("")
            
            if arch.get("inconsistencies"):
                report_lines.append("### Inconsistencias:")
                for item in arch["inconsistencies"][:3]:
                    report_lines.append(f"  - [{item.get('severity', 'N/A')}] {item.get('description', 'N/A')}")
                report_lines.append("")
        
        # Código
        if "code" in validation_results:
            code = validation_results["code"]
            report_lines.append("## 2. VALIDACIÓN DE CÓDIGO")
            report_lines.append(f"Score: {code.get('code_quality_score', 0)}/10")
            report_lines.append("")
            
            if code.get("potential_errors"):
                report_lines.append("### Errores potenciales:")
                for item in code["potential_errors"][:3]:
                    report_lines.append(f"  - [{item.get('severity', 'N/A')}] {item.get('description', 'N/A')}")
                report_lines.append("")
        
        # Seguridad
        if "security" in validation_results:
            sec = validation_results["security"]
            report_lines.append("## 3. ANÁLISIS DE SEGURIDAD")
            report_lines.append(f"Score: {sec.get('security_score', 0)}/10")
            report_lines.append("")
            
            if sec.get("vulnerabilities"):
                report_lines.append("### Vulnerabilidades:")
                for item in sec["vulnerabilities"][:3]:
                    report_lines.append(f"  - [{item.get('severity', 'N/A')}] {item.get('description', 'N/A')}")
                report_lines.append("")
        
        # Optimizaciones
        if "optimizations" in validation_results:
            opt = validation_results["optimizations"]
            report_lines.append("## 4. OPTIMIZACIONES SUGERIDAS")
            report_lines.append("")
            
            if opt.get("priority_optimizations"):
                report_lines.append("### Prioridades:")
                for item in opt["priority_optimizations"][:5]:
                    report_lines.append(f"  - {item}")
                report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append("FIN DEL REPORTE")
        
        return "\n".join(report_lines)
        
