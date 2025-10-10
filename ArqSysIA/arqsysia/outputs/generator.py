"""
Output Generator - Generador de Documentos Finales

Genera documentos markdown profesionales a partir del ProjectState:
1. mvp_proposal.md - Propuesta de MVP para clientes
2. technical_architecture.md - Documentación técnica completa
3. validation_report.md - Reporte de validación detallado
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from arqsysia.core.state import ProjectState


class OutputGenerator:
    """
    Genera documentos finales en formato markdown.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el generador de outputs.
        
        Args:
            output_dir: Directorio donde guardar los documentos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_all(self, state: ProjectState) -> Dict[str, Path]:
        """
        Genera todos los documentos para un proyecto.
        
        Args:
            state: Estado del proyecto con todos los análisis
            
        Returns:
            Dict con nombres de documentos y sus rutas
        """
        print("\n" + "="*60)
        print("📄 GENERANDO DOCUMENTOS FINALES")
        print("="*60)
        print()
        
        generated_docs = {}
        
        # 1. Propuesta de MVP
        print("1️⃣  Generando propuesta de MVP...")
        mvp_path = self.generate_mvp_proposal(state)
        generated_docs["mvp_proposal"] = mvp_path
        print(f"   ✅ {mvp_path}")
        
        # 2. Arquitectura técnica
        print("\n2️⃣  Generando documentación técnica...")
        tech_path = self.generate_technical_architecture(state)
        generated_docs["technical_architecture"] = tech_path
        print(f"   ✅ {tech_path}")
        
        # 3. Reporte de validación
        if state.get_output("validation_complete"):
            print("\n3️⃣  Generando reporte de validación...")
            val_path = self.generate_validation_report(state)
            generated_docs["validation_report"] = val_path
            print(f"   ✅ {val_path}")
        
        print("\n" + "="*60)
        print(f"✅ {len(generated_docs)} documentos generados")
        print("="*60)
        print()
        
        return generated_docs
    
    def generate_mvp_proposal(self, state: ProjectState) -> Path:
        """
        Genera propuesta de MVP para clientes (no técnico).
        
        Enfocado en valor de negocio, alcance, y roadmap.
        """
        analysis = state.get_output("analysis") or state.get_output("architecture_analysis") or {}
        
        content = []
        
        # Header
        content.append(f"# Propuesta de MVP: {state.project_name}")
        content.append("")
        content.append(f"**Fecha:** {datetime.now().strftime('%d de %B, %Y')}")
        content.append(f"**Generado por:** ArqSysIA")
        content.append("")
        content.append("---")
        content.append("")
        
        # 1. Resumen Ejecutivo
        content.append("## 1. Resumen Ejecutivo")
        content.append("")
        content.append(f"Este documento presenta la propuesta de Producto Mínimo Viable (MVP) para **{state.project_name}**.")
        content.append("")
        
        pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
        content.append(f"**Arquitectura propuesta:** {pattern}")
        content.append("")
        
        # 2. Requerimientos Funcionales
        content.append("## 2. Requerimientos Funcionales")
        content.append("")
        
        functional = analysis.get('functional_requirements', [])
        if functional:
            content.append("El MVP incluirá las siguientes funcionalidades:")
            content.append("")
            for i, req in enumerate(functional, 1):
                content.append(f"{i}. {req}")
            content.append("")
        
        # 3. Requerimientos No Funcionales
        content.append("## 3. Requerimientos No Funcionales")
        content.append("")
        
        non_functional = analysis.get('non_functional_requirements', [])
        if non_functional:
            for req in non_functional:
                content.append(f"- {req}")
            content.append("")
        
        # 4. Stack Tecnológico
        content.append("## 4. Stack Tecnológico Propuesto")
        content.append("")
        
        stack = analysis.get('technology_stack') or analysis.get('tech_stack', {})
        if stack:
            for category, tech in stack.items():
                if isinstance(tech, list):
                    tech_str = ", ".join(tech)
                    content.append(f"- **{category}:** {tech_str}")
                else:
                    content.append(f"- **{category}:** {tech}")
            content.append("")
        
        # 5. Componentes Principales
        content.append("## 5. Componentes del Sistema")
        content.append("")
        
        components = analysis.get('main_components') or analysis.get('components', [])
        if components:
            for comp in components:
                if isinstance(comp, dict):
                    name = comp.get('name') or comp.get('component', 'N/A')
                    desc = comp.get('description', '')
                    content.append(f"### {name}")
                    if desc:
                        content.append(desc)
                    content.append("")
                elif isinstance(comp, str):
                    content.append(f"### {comp}")
                    content.append("")
        
        # 6. Alcance del MVP
        content.append("## 6. Alcance del MVP")
        content.append("")
        
        mvp_scope = analysis.get('mvp_scope', {})
        if mvp_scope:
            # Manejar si mvp_scope es dict o list
            if isinstance(mvp_scope, dict):
                included = mvp_scope.get('included_features', [])
                excluded = mvp_scope.get('excluded_features', [])
                
                if included:
                    content.append("### ✅ Incluido en el MVP")
                    content.append("")
                    for feature in included:
                        content.append(f"- {feature}")
                    content.append("")
                
                if excluded:
                    content.append("### ⏸️ Excluido del MVP (para versiones futuras)")
                    content.append("")
                    for feature in excluded:
                        content.append(f"- {feature}")
                    content.append("")
            elif isinstance(mvp_scope, list):
                # Si es lista, asumimos que son features incluidas
                content.append("### ✅ Funcionalidades del MVP")
                content.append("")
                for feature in mvp_scope:
                    content.append(f"- {feature}")
                content.append("")
        
        # 7. Roadmap
        content.append("## 7. Roadmap del Producto")
        content.append("")
        
        roadmap = analysis.get('product_roadmap', [])
        if roadmap:
            for i, phase in enumerate(roadmap, 1):
                if isinstance(phase, dict):
                    phase_name = phase.get('phase', f'Fase {i}')
                    features = phase.get('features', [])
                    timeline = phase.get('timeline', '')
                    
                    content.append(f"### {phase_name}")
                    if timeline:
                        content.append(f"**Timeline:** {timeline}")
                    content.append("")
                    if features:
                        for feature in features:
                            content.append(f"- {feature}")
                        content.append("")
                elif isinstance(phase, str):
                    # Si roadmap es una lista de strings
                    content.append(f"### Fase {i}")
                    content.append(f"- {phase}")
                    content.append("")
        
        # 8. Próximos Pasos
        content.append("## 8. Próximos Pasos")
        content.append("")
        content.append("1. **Revisión de la propuesta** - Validar requerimientos y alcance")
        content.append("2. **Aprobación del stack tecnológico** - Confirmar tecnologías seleccionadas")
        content.append("3. **Planificación de sprints** - Definir iteraciones de desarrollo")
        content.append("4. **Inicio de desarrollo** - Implementación del MVP")
        content.append("")
        
        content.append("---")
        content.append("")
        content.append("*Documento generado automáticamente por ArqSysIA*")
        
        # Guardar archivo
        filename = f"{state.project_name.lower().replace(' ', '_')}_mvp_proposal.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return filepath
    
    def generate_technical_architecture(self, state: ProjectState) -> Path:
        """
        Genera documentación técnica completa.
        
        Incluye arquitectura detallada, diagramas (texto), y decisiones técnicas.
        """
        analysis = state.get_output("analysis") or state.get_output("architecture_analysis") or {}
        
        content = []
        
        # Header
        content.append(f"# Arquitectura Técnica: {state.project_name}")
        content.append("")
        content.append(f"**Fecha:** {datetime.now().strftime('%d de %B, %Y')}")
        content.append(f"**Versión:** 1.0")
        content.append("")
        content.append("---")
        content.append("")
        
        # TOC
        content.append("## Tabla de Contenidos")
        content.append("")
        content.append("1. [Visión General](#visión-general)")
        content.append("2. [Patrón Arquitectural](#patrón-arquitectural)")
        content.append("3. [Stack Tecnológico](#stack-tecnológico)")
        content.append("4. [Componentes del Sistema](#componentes-del-sistema)")
        content.append("5. [Estructura de Archivos](#estructura-de-archivos)")
        content.append("6. [Dependencias](#dependencias)")
        content.append("7. [Consideraciones de Deployment](#consideraciones-de-deployment)")
        content.append("")
        content.append("---")
        content.append("")
        
        # 1. Visión General
        content.append("## Visión General")
        content.append("")
        content.append(f"**Proyecto:** {state.project_name}")
        content.append("")
        content.append("**Requerimientos originales:**")
        content.append("```")
        content.append(state.original_requirements[:500] + "..." if len(state.original_requirements) > 500 else state.original_requirements)
        content.append("```")
        content.append("")
        
        # 2. Patrón Arquitectural
        content.append("## Patrón Arquitectural")
        content.append("")
        
        pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
        justification = analysis.get('justification') or analysis.get('architecture_justification', '')
        
        content.append(f"**Patrón seleccionado:** {pattern}")
        content.append("")
        
        if justification:
            content.append("**Justificación:**")
            content.append("")
            content.append(justification)
            content.append("")
        
        # 3. Stack Tecnológico
        content.append("## Stack Tecnológico")
        content.append("")
        
        stack = analysis.get('technology_stack') or analysis.get('tech_stack', {})
        if stack:
            for category, tech in stack.items():
                if isinstance(tech, list):
                    content.append(f"### {category}")
                    content.append("")
                    for t in tech:
                        content.append(f"- {t}")
                    content.append("")
                else:
                    content.append(f"### {category}")
                    content.append("")
                    content.append(f"- {tech}")
                    content.append("")
        
        # 4. Componentes del Sistema
        content.append("## Componentes del Sistema")
        content.append("")
        
        components = analysis.get('main_components') or analysis.get('components', [])
        if components:
            for comp in components:
                if isinstance(comp, dict):
                    name = comp.get('name') or comp.get('component', 'N/A')
                    desc = comp.get('description', '')
                    responsibilities = comp.get('responsibilities', [])
                    
                    content.append(f"### {name}")
                    content.append("")
                    if desc:
                        content.append(f"**Descripción:** {desc}")
                        content.append("")
                    
                    if responsibilities:
                        content.append("**Responsabilidades:**")
                        content.append("")
                        for resp in responsibilities:
                            content.append(f"- {resp}")
                        content.append("")
        
        # 5. Estructura de Archivos
        content.append("## Estructura de Archivos")
        content.append("")
        
        file_structure = state.get_output("file_structure")
        if file_structure:
            content.append("```")
            content.append(self._format_file_structure(file_structure))
            content.append("```")
            content.append("")
        
        # 6. Dependencias
        content.append("## Dependencias")
        content.append("")
        
        dependencies = analysis.get('dependencies', {})
        if dependencies:
            # Manejar dict o list
            if isinstance(dependencies, dict):
                for dep_type, deps in dependencies.items():
                    content.append(f"### {dep_type}")
                    content.append("")
                    if isinstance(deps, list):
                        for dep in deps:
                            content.append(f"- {dep}")
                    elif isinstance(deps, dict):
                        for name, version in deps.items():
                            content.append(f"- {name}: {version}")
                    content.append("")
            elif isinstance(dependencies, list):
                content.append("### Dependencias del Proyecto")
                content.append("")
                for dep in dependencies:
                    content.append(f"- {dep}")
                content.append("")
        
        # 7. Deployment
        content.append("## Consideraciones de Deployment")
        content.append("")
        
        deployment = analysis.get('deployment_considerations', {})
        if deployment:
            # Manejar dict o string
            if isinstance(deployment, dict):
                strategy = deployment.get('strategy', '')
                if strategy:
                    content.append(f"**Estrategia:** {strategy}")
                    content.append("")
                
                requirements = deployment.get('requirements', [])
                if requirements:
                    content.append("**Requerimientos:**")
                    content.append("")
                    for req in requirements:
                        content.append(f"- {req}")
                    content.append("")
            elif isinstance(deployment, str):
                content.append(deployment)
                content.append("")
            elif isinstance(deployment, list):
                content.append("**Consideraciones:**")
                content.append("")
                for item in deployment:
                    content.append(f"- {item}")
                content.append("")
        
        content.append("---")
        content.append("")
        content.append("*Documento generado automáticamente por ArqSysIA*")
        
        # Guardar archivo
        filename = f"{state.project_name.lower().replace(' ', '_')}_technical_architecture.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return filepath
    
    def generate_validation_report(self, state: ProjectState) -> Path:
        """
        Genera reporte detallado de validación.
        
        Incluye scores, issues encontrados, y recomendaciones.
        """
        validation_results = state.get_output("validation_results", {})
        
        content = []
        
        # Header
        content.append(f"# Reporte de Validación: {state.project_name}")
        content.append("")
        content.append(f"**Fecha:** {datetime.now().strftime('%d de %B, %Y')}")
        content.append(f"**Generado por:** ArqSysIA Validator")
        content.append("")
        content.append("---")
        content.append("")
        
        # Resumen de Scores
        content.append("## Resumen de Scores")
        content.append("")
        
        arch = validation_results.get("architecture", {})
        code = validation_results.get("code", {})
        sec = validation_results.get("security", {})
        
        content.append("| Área | Score | Estado |")
        content.append("|------|-------|--------|")
        
        arch_score = arch.get("architecture_score", 0)
        arch_status = "✅ Bueno" if arch_score >= 7 else "⚠️ Mejorable" if arch_score >= 5 else "❌ Requiere atención"
        content.append(f"| Arquitectura | {arch_score}/10 | {arch_status} |")
        
        if code:
            code_score = code.get("code_quality_score", 0)
            code_status = "✅ Bueno" if code_score >= 7 else "⚠️ Mejorable" if code_score >= 5 else "❌ Requiere atención"
            content.append(f"| Calidad de Código | {code_score}/10 | {code_status} |")
        
        sec_score = sec.get("security_score", 0)
        sec_status = "✅ Bueno" if sec_score >= 7 else "⚠️ Mejorable" if sec_score >= 5 else "❌ Requiere atención"
        content.append(f"| Seguridad | {sec_score}/10 | {sec_status} |")
        
        content.append("")
        content.append("---")
        content.append("")
        
        # 1. Validación de Arquitectura
        content.append("## 1. Validación de Arquitectura")
        content.append("")
        
        assessment = arch.get("overall_assessment", "N/A")
        content.append(f"**Evaluación general:** {assessment}")
        content.append("")
        
        # Inconsistencias
        inconsistencies = arch.get("inconsistencies", [])
        if inconsistencies:
            content.append("### ⚠️ Inconsistencias Encontradas")
            content.append("")
            for inc in inconsistencies:
                severity = inc.get("severity", "N/A")
                component = inc.get("component", "N/A")
                description = inc.get("description", "N/A")
                impact = inc.get("impact", "N/A")
                
                content.append(f"**[{severity.upper()}] {component}**")
                content.append(f"- **Problema:** {description}")
                content.append(f"- **Impacto:** {impact}")
                content.append("")
        
        # Errores de diseño
        design_errors = arch.get("design_errors", [])
        if design_errors:
            content.append("### 🔴 Errores de Diseño")
            content.append("")
            for err in design_errors:
                severity = err.get("severity", "N/A")
                area = err.get("area", "N/A")
                description = err.get("description", "N/A")
                recommendation = err.get("recommendation", "N/A")
                
                content.append(f"**[{severity.upper()}] {area}**")
                content.append(f"- **Descripción:** {description}")
                content.append(f"- **Recomendación:** {recommendation}")
                content.append("")
        
        # Componentes faltantes
        missing = arch.get("missing_components", [])
        if missing:
            content.append("### 📦 Componentes Faltantes")
            content.append("")
            for comp in missing:
                component = comp.get("component", "N/A")
                reason = comp.get("reason", "N/A")
                priority = comp.get("priority", "N/A")
                
                content.append(f"**{component}** (Prioridad: {priority})")
                content.append(f"- {reason}")
                content.append("")
        
        # Mejoras
        improvements = arch.get("improvements", [])
        if improvements:
            content.append("### 💡 Mejoras Sugeridas")
            content.append("")
            for imp in improvements:
                area = imp.get("area", "N/A")
                suggestion = imp.get("suggestion", "N/A")
                benefit = imp.get("benefit", "N/A")
                
                content.append(f"**{area}**")
                content.append(f"- **Sugerencia:** {suggestion}")
                content.append(f"- **Beneficio:** {benefit}")
                content.append("")
        
        # 2. Validación de Código
        if code:
            content.append("## 2. Validación de Código")
            content.append("")
            
            # Errores potenciales
            errors = code.get("potential_errors", [])
            if errors:
                content.append("### 🐛 Errores Potenciales")
                content.append("")
                for err in errors:
                    severity = err.get("severity", "N/A")
                    file = err.get("file", "N/A")
                    description = err.get("description", "N/A")
                    fix = err.get("fix", "N/A")
                    
                    content.append(f"**[{severity.upper()}] {file}**")
                    content.append(f"- **Problema:** {description}")
                    content.append(f"- **Solución:** {fix}")
                    content.append("")
            
            # Code smells
            smells = code.get("code_smells", [])
            if smells:
                content.append("### 👃 Code Smells")
                content.append("")
                for smell in smells:
                    file = smell.get("file", "N/A")
                    smell_type = smell.get("smell", "N/A")
                    description = smell.get("description", "N/A")
                    refactor = smell.get("refactor_suggestion", "N/A")
                    
                    content.append(f"**{file}** - {smell_type}")
                    content.append(f"- **Descripción:** {description}")
                    content.append(f"- **Refactorización:** {refactor}")
                    content.append("")
        
        # 3. Análisis de Seguridad
        content.append("## 3. Análisis de Seguridad")
        content.append("")
        
        # Vulnerabilidades
        vulnerabilities = sec.get("vulnerabilities", [])
        if vulnerabilities:
            content.append("### 🔒 Vulnerabilidades Identificadas")
            content.append("")
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "N/A")
                category = vuln.get("category", "N/A")
                description = vuln.get("description", "N/A")
                mitigation = vuln.get("mitigation", "N/A")
                
                content.append(f"**[{severity.upper()}] {category}**")
                content.append(f"- **Descripción:** {description}")
                content.append(f"- **Mitigación:** {mitigation}")
                content.append("")
        
        # Prácticas faltantes
        missing_practices = sec.get("missing_practices", [])
        if missing_practices:
            content.append("### 📋 Prácticas de Seguridad Faltantes")
            content.append("")
            for practice in missing_practices:
                name = practice.get("practice", "N/A")
                importance = practice.get("importance", "N/A")
                implementation = practice.get("implementation", "N/A")
                
                content.append(f"**{name}**")
                content.append(f"- **Importancia:** {importance}")
                content.append(f"- **Implementación:** {implementation}")
                content.append("")
        
        # Recomendaciones prioritarias
        recommendations = sec.get("priority_recommendations", [])
        if recommendations:
            content.append("### ⭐ Recomendaciones Prioritarias")
            content.append("")
            for rec in recommendations:
                priority = rec.get("priority", 0)
                recommendation = rec.get("recommendation", "N/A")
                impact = rec.get("impact", "N/A")
                
                content.append(f"**Prioridad {priority}:** {recommendation}")
                content.append(f"- **Impacto:** {impact}")
                content.append("")
        
        # 4. Optimizaciones
        optimizations = validation_results.get("optimizations", {})
        if optimizations:
            content.append("## 4. Sugerencias de Optimización")
            content.append("")
            
            priority_opts = optimizations.get("priority_optimizations", [])
            if priority_opts:
                content.append("### 🚀 Optimizaciones Prioritarias")
                content.append("")
                for opt in priority_opts:
                    content.append(f"- {opt}")
                content.append("")
        
        content.append("---")
        content.append("")
        content.append("*Reporte generado automáticamente por ArqSysIA Validator*")
        
        # Guardar archivo
        filename = f"{state.project_name.lower().replace(' ', '_')}_validation_report.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return filepath
    
    def _format_file_structure(self, structure, indent: int = 0) -> str:
        """
        Formatea la estructura de archivos como texto.
        
        Maneja tanto dict como otros formatos.
        """
        if isinstance(structure, dict):
            lines = []
            for key, value in structure.items():
                lines.append("  " * indent + key + "/")
                if isinstance(value, dict):
                    lines.append(self._format_file_structure(value, indent + 1))
            return "\n".join(lines)
        elif isinstance(structure, str):
            return structure
        else:
            return str(structure)


def create_generator(output_dir: str = "output") -> OutputGenerator:
    """
    Factory function para crear un OutputGenerator.
    
    Args:
        output_dir: Directorio de salida
        
    Returns:
        OutputGenerator configurado
    """
    return OutputGenerator(output_dir=output_dir)
    
