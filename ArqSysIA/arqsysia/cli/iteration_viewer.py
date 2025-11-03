"""
Iteration Viewer - Visualización de iteraciones.

Proporciona visualización de:
- Historial completo de iteraciones
- Detalles de iteración individual
- Resumen de proyecto
"""

from typing import List, Dict, Any
from datetime import datetime

from arqsysia.core.state import Iteration
from arqsysia.core import VersionManager, IterationResult
from arqsysia.storage.base import StorageBackend


class IterationViewer:
    """
    Visualizador de iteraciones.
    
    Muestra:
    - Historial de iteraciones en formato tabla
    - Detalles de iteración individual
    - Estadísticas y tendencias del proyecto
    
    Example:
        >>> viewer = IterationViewer("MyProject", storage)
        >>> viewer.show_iteration_history()
        >>> viewer.show_iteration_details(1)
    """
    
    def __init__(self, project_name: str, storage: StorageBackend):
        """
        Inicializar viewer.
        
        Args:
            project_name: Nombre del proyecto
            storage: Backend de almacenamiento
        """
        self.project_name = project_name
        self.version_manager = VersionManager(project_name, storage)
    
    def _get_overall_score(self, validation_output: Dict[str, Any]) -> int:
        """
        Calcula el overall score desde validation_results.
        
        La estructura real es:
        validation_output = {
            "validation": None,  # Este está vacío
            "validation_results": {
                "architecture": {"architecture_score": 6},
                "security": {"security_score": 4}
            }
        }
        
        Args:
            validation_output: Diccionario de validation desde state.outputs
            
        Returns:
            Score promedio de 0-100, o 0 si no hay datos
        """
        # Primero intentar obtener desde validation_results
        validation_results = validation_output.get('validation_results', {})
        
        if validation_results:
            scores = []
            
            # Architecture score
            arch = validation_results.get('architecture', {})
            if 'architecture_score' in arch:
                scores.append(arch['architecture_score'] * 10)  # Convertir de 0-10 a 0-100
            
            # Security score
            security = validation_results.get('security', {})
            if 'security_score' in security:
                scores.append(security['security_score'] * 10)  # Convertir de 0-10 a 0-100
            
            # Calcular promedio
            if scores:
                return int(sum(scores) / len(scores))
        
        # Si no hay validation_results, intentar desde validation directamente
        validation = validation_output.get('validation', {})
        if validation and 'overall_score' in validation:
            return validation['overall_score']
        
        return 0
    
    def show_iteration_history(self) -> None:
        """
        Mostrar historial completo de iteraciones en formato tabla.
        
        Muestra:
        - Número de iteración
        - Fecha
        - Score de validación
        - Iteración padre (si existe)
        - Tipo de iteración
        - Estadísticas generales
        """
        iterations = self.version_manager.list_iterations()
        
        if not iterations:
            print("\n🔭 No iterations found.")
            print("💡 Use 'New Iteration' to create your first iteration.")
            return
        
        # Header
        print("\n╔" + "═" * 70 + "╗")
        print("║" + f" Iteration History - {self.project_name} ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        # Tabla
        print("┌─────┬──────────────────┬─────────┬────────┬─────────────┐")
        print("│  #  │ Date             │  Score  │ Parent │ Type        │")
        print("├─────┼──────────────────┼─────────┼────────┼─────────────┤")
        
        for iteration in iterations:
            # Usar created_at en lugar de state.timestamp
            date_str = iteration.created_at.strftime("%Y-%m-%d %H:%M")
            
            # ✅ CORRECCIÓN: Calcular score correctamente desde validation_results
            validation_output = iteration.state.outputs.get('validation', {})
            score_val = self._get_overall_score(validation_output)
            score = f"{score_val}/100"
            
            # Usar state.parent_iteration
            parent = str(iteration.state.parent_iteration) if iteration.state.parent_iteration else "-"
            
            # Determinar tipo de iteración
            iter_type = self._determine_iteration_type(iteration)
            
            # Usar iteration_number
            print(f"│ {iteration.iteration_number:>3} │ {date_str:<16} │ {score:>7} │ {parent:>6} │ {iter_type:<11} │")
        
        print("└─────┴──────────────────┴─────────┴────────┴─────────────┘\n")
        
        # Estadísticas
        self._show_statistics(iterations)
    
    def show_iteration_details(self, iteration_number: int) -> None:
        """
        Mostrar detalles completos de una iteración específica.
        
        Args:
            iteration_number: Número de iteración a mostrar
        
        Raises:
            FileNotFoundError: Si la iteración no existe
        """
        iteration = self.version_manager.get_iteration(iteration_number)
        
        # Header
        print("\n╔" + "═" * 70 + "╗")
        print("║" + f" Iteration {iteration_number} - Details ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        # Información básica
        print("📋 BASIC INFORMATION")
        print("─" * 70)
        # Usar created_at
        print(f"Date: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        # Usar state.parent_iteration
        print(f"Parent Iteration: {iteration.state.parent_iteration if iteration.state.parent_iteration else 'None (initial)'}")
        
        # ✅ CORRECCIÓN: Calcular score correctamente
        validation_output = iteration.state.outputs.get('validation', {})
        score = self._get_overall_score(validation_output)
        print(f"Validation Score: {score}/100")
        
        # ✅ CORRECCIÓN: Arquitectura - acceder a la estructura anidada correcta
        print("\n🗏️  ARCHITECTURE")
        print("─" * 70)
        
        # La estructura real es: outputs -> analysis -> analysis -> {architecture_pattern, tech_stack, etc}
        analysis_output = iteration.state.outputs.get('analysis', {})
        analysis_data = analysis_output.get('analysis', {})
        
        if analysis_data:
            # Extraer campos específicos
            pattern = analysis_data.get('architecture_pattern', 'N/A')
            justification = analysis_data.get('architecture_justification', 'N/A')
            tech_stack = analysis_data.get('tech_stack', {})
            
            print(f"  • Pattern: {pattern}")
            # Truncar justificación si es muy larga
            if len(justification) > 200:
                print(f"  • Justification: {justification[:200]}...")
            else:
                print(f"  • Justification: {justification}")
            
            print(f"  • Tech Stack:")
            for key, value in tech_stack.items():
                print(f"    - {key}: {value}")
        else:
            print("  No architecture details available")
        
        # ✅ BUG FIX #2: Validar que analysis_data no sea None antes de usar .get()
        print(f"\n📦 COMPONENTS")
        print("─" * 70)
        
        # Validación agregada para evitar crash con iteraciones fallidas
        if analysis_data:
            components = analysis_data.get('main_components', [])
        else:
            components = []
        
        if components:
            print(f"Total: {len(components)}\n")
            for i, comp in enumerate(components, 1):
                if isinstance(comp, dict):
                    comp_name = comp.get('name', 'Unknown')
                    comp_desc = comp.get('description', '')
                    responsibilities = comp.get('responsibilities', [])
                    
                    print(f"  {i}. {comp_name}")
                    if comp_desc:
                        # Truncar descripción larga
                        if len(comp_desc) > 100:
                            print(f"     {comp_desc[:100]}...")
                        else:
                            print(f"     {comp_desc}")
                    
                    if responsibilities:
                        print(f"     Responsibilities:")
                        for resp in responsibilities[:3]:
                            print(f"       - {resp}")
                        if len(responsibilities) > 3:
                            print(f"       ... and {len(responsibilities) - 3} more")
                    print()
        else:
            print("  No components available")
        
        # Código generado
        print(f"\n💻 CODE GENERATION")
        print("─" * 70)
        
        code_output = iteration.state.outputs.get('code_generation', {})
        if code_output:
            files_generated = code_output.get('files_generated', [])
            print(f"Files Generated: {len(files_generated)}")
            
            if files_generated:
                print("\nKey Files:")
                for file_path in files_generated[:5]:
                    print(f"  • {file_path}")
                if len(files_generated) > 5:
                    print(f"  ... and {len(files_generated) - 5} more files")
        else:
            print("  No code generation details available")
        
        # Validación detallada
        self._show_validation_details(iteration)
    
    def show_iteration_result(self, result: IterationResult) -> None:
        """
        Mostrar resultado de iteración recién completada.
        
        Args:
            result: Resultado de la iteración
        """
        print("\n╔" + "═" * 70 + "╗")
        print("║" + " Iteration Result ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        # Score
        print(f"📊 Final Score: {result.final_score}/100")
        print(self._create_score_bar(result.final_score))
        
        # Issues
        issues = result.validation_issues
        if issues:
            print(f"\n⚠️  Issues Found: {len(issues)}")
            for i, issue in enumerate(issues[:3], 1):
                severity = issue.get('severity', 'unknown')
                desc = issue.get('description', 'Unknown issue')
                print(f"   {i}. [{severity}] {desc}")
            
            if len(issues) > 3:
                print(f"   ... and {len(issues) - 3} more issues")
        else:
            print("\n✅ No issues found!")
        
        # Timestamp
        print(f"\n🕐 Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _determine_iteration_type(self, iteration: Iteration) -> str:
        """
        Determinar tipo de iteración basado en parent y decisiones.
        
        Args:
            iteration: Iteración a analizar
        
        Returns:
            Tipo de iteración: 'Initial', 'Regenerate', 'Redesign', 'Unknown'
        """
        if iteration.state.parent_iteration is None:
            return "Initial"
        
        # Buscar en decisiones
        for decision in iteration.decisions:
            if decision.iteration_number == iteration.iteration_number:
                if decision.decision_type == "code_regenerated":
                    return "Regenerate"
                elif decision.decision_type == "architecture_redesigned":
                    return "Redesign"
        
        return "Update"
    
    def _show_statistics(self, iterations: List[Iteration]) -> None:
        """
        Mostrar estadísticas generales del proyecto.
        
        Args:
            iterations: Lista de iteraciones
        """
        if not iterations:
            return
        
        # Calcular estadísticas
        total = len(iterations)
        
        # ✅ CORRECCIÓN: Calcular scores correctamente desde validation_results
        scores = []
        for i in iterations:
            validation_output = i.state.outputs.get('validation', {})
            score = self._get_overall_score(validation_output)
            scores.append(score)
        
        avg_score = sum(scores) / total if scores else 0
        trend = self._calculate_trend(iterations)
        
        # ✅ CORRECCIÓN: Mejor y peor iteración usando la función helper
        def get_score(iteration):
            validation_output = iteration.state.outputs.get('validation', {})
            return self._get_overall_score(validation_output)
        
        best = max(iterations, key=get_score)
        worst = min(iterations, key=get_score)
        best_score = get_score(best)
        worst_score = get_score(worst)
        
        # Mostrar
        print("📊 STATISTICS")
        print("─" * 70)
        print(f"Total Iterations: {total}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Trend: {trend}")
        print(f"Best Iteration: #{best.iteration_number} ({best_score}/100)")
        print(f"Worst Iteration: #{worst.iteration_number} ({worst_score}/100)")
    
    def _show_validation_details(self, iteration: Iteration) -> None:
        """
        Mostrar detalles de validación de una iteración.
        
        Args:
            iteration: Iteración con detalles de validación
        """
        print("\n✅ VALIDATION DETAILS")
        print("─" * 70)
        
        # ✅ CORRECCIÓN: Acceder desde validation_results
        validation_output = iteration.state.outputs.get('validation', {})
        validation_results = validation_output.get('validation_results', {})
        
        if not validation_results:
            print("No validation details available")
            return
        
        # Architecture score
        arch = validation_results.get('architecture', {})
        arch_score = arch.get('architecture_score', 0)
        print(f"Architecture Score: {arch_score}/10")
        
        # Security score
        security = validation_results.get('security', {})
        security_score = security.get('security_score', 0)
        print(f"Security Score: {security_score}/10")
        
        # Overall (calculado)
        overall = self._get_overall_score(validation_output)
        print(f"Overall Score: {overall}/100")
        
        # Architecture issues
        inconsistencies = arch.get('inconsistencies', [])
        design_errors = arch.get('design_errors', [])
        missing_components = arch.get('missing_components', [])
        
        total_arch_issues = len(inconsistencies) + len(design_errors) + len(missing_components)
        
        if total_arch_issues > 0:
            print(f"\nArchitecture Issues ({total_arch_issues}):")
            
            for issue in inconsistencies[:2]:
                severity = issue.get('severity', 'unknown')
                desc = issue.get('description', 'Unknown issue')
                print(f"  • [{severity.upper()}] {desc}")
            
            for error in design_errors[:2]:
                severity = error.get('severity', 'unknown')
                desc = error.get('description', 'Unknown error')
                print(f"  • [{severity.upper()}] {desc}")
            
            remaining = total_arch_issues - 4
            if remaining > 0:
                print(f"  ... and {remaining} more issues")
        
        # Security vulnerabilities
        vulnerabilities = security.get('vulnerabilities', [])
        if vulnerabilities:
            print(f"\nSecurity Vulnerabilities ({len(vulnerabilities)}):")
            for vuln in vulnerabilities[:3]:
                severity = vuln.get('severity', 'unknown')
                desc = vuln.get('description', 'Unknown vulnerability')
                print(f"  • [{severity.upper()}] {desc}")
            
            if len(vulnerabilities) > 3:
                print(f"  ... and {len(vulnerabilities) - 3} more vulnerabilities")
        
        # Optimizations
        optimizations = validation_results.get('optimizations', {})
        if optimizations:
            priority_opts = optimizations.get('priority_optimizations', [])
            if priority_opts:
                print(f"\n💡 Priority Optimizations ({len(priority_opts)}):")
                for i, opt in enumerate(priority_opts[:3], 1):
                    print(f"  {i}. {opt}")
                
                if len(priority_opts) > 3:
                    print(f"  ... and {len(priority_opts) - 3} more optimizations")
    
    def _calculate_trend(self, iterations: List[Iteration]) -> str:
        """
        Calcular tendencia de scores a lo largo de las iteraciones.
        
        Args:
            iterations: Lista de iteraciones ordenadas
        
        Returns:
            Tendencia: '↗ Improving', '↘ Declining', '→ Stable'
        """
        if len(iterations) < 2:
            return "→ Stable (need more iterations)"
        
        # ✅ CORRECCIÓN: Usar función helper para obtener scores
        first_score = self._get_overall_score(iterations[0].state.outputs.get('validation', {}))
        last_score = self._get_overall_score(iterations[-1].state.outputs.get('validation', {}))
        
        diff = last_score - first_score
        
        if diff > 5:
            return "↗ Improving"
        elif diff < -5:
            return "↘ Declining"
        else:
            return "→ Stable"
    
    def _create_score_bar(self, score: int, width: int = 50) -> str:
        """
        Crear barra visual de score.
        
        Args:
            score: Score de 0-100
            width: Ancho de la barra en caracteres
        
        Returns:
            Barra visual ASCII
        """
        filled = int((score / 100) * width)
        empty = width - filled
        
        # Colorear según score (usando caracteres ASCII)
        if score >= 80:
            bar_char = "█"  # Excelente
        elif score >= 60:
            bar_char = "▓"  # Bueno
        elif score >= 40:
            bar_char = "▒"  # Regular
        else:
            bar_char = "░"  # Bajo
        
        bar = bar_char * filled + "·" * empty
        return f"[{bar}]"
        
