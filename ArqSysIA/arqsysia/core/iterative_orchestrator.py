"""
Iterative Orchestrator - Coordinador Iterativo para ArqSysIA v1.0

Orquesta el flujo completo de iteraciones con feedback loops:
1. Analyzer → CodeGen → Validator
2. Menú post-validación interactivo
3. Regeneración de código con feedback
4. Rediseño de arquitectura
5. Persistencia automática de iteraciones

Características:
- Coordinación de Enhanced Phases (con contexto histórico)
- Feedback loops completos
- Menú interactivo post-validación
- Registro automático de decisiones
- Manejo robusto de errores
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from arqsysia.core import (
    VersionManager,
    DecisionLogger,
    DiffEngine,
    ProjectState,
    Iteration,
    Decision
)
from arqsysia.phases import (
    EnhancedAnalyzer,
    EnhancedCodeGen,
    EnhancedValidator
)


@dataclass
class IterationResult:
    """Resultado de una iteración completa"""
    iteration: int
    project_name: str
    analysis: Dict[str, Any]
    codegen: Dict[str, Any]
    validation: Dict[str, Any]
    timestamp: datetime
    duration_seconds: float = 0.0
    phase_durations: Dict[str, float] = field(default_factory=dict)
    
    def get_final_scores(self) -> Dict[str, int]:
        """Extrae los scores finales de la validación"""
        validation = self.validation
        if 'scores' in validation:
            return validation['scores']
        return {}
    
    def has_issues(self) -> bool:
        """Verifica si hay issues reportados"""
        validation = self.validation
        if 'issues' in validation:
            return len(validation['issues']) > 0
        return False
    
    def get_issues_count(self) -> int:
        """Retorna la cantidad de issues detectados"""
        validation = self.validation
        if 'issues' in validation:
            return len(validation['issues'])
        return 0


class IterativeOrchestrator:
    """
    Orquestador iterativo que coordina las Enhanced Phases en un flujo
    completo con feedback loops y menú post-validación.
    """
    
    def __init__(self, project_name: str, storage):
        """
        Inicializa el orquestador iterativo.
        
        Args:
            project_name: Nombre del proyecto
            storage: Backend de almacenamiento (FileStorage o SQLiteStorage)
        """
        self.project_name = project_name
        self.storage = storage
        
        # Core components
        self.version_manager = VersionManager(project_name, storage)
        self.decision_logger = DecisionLogger(project_name, storage)
        self.diff_engine = DiffEngine()
        
        # Enhanced Phases (con contexto histórico)
        self.analyzer = EnhancedAnalyzer(
            self.version_manager,
            self.decision_logger,
            self.diff_engine
        )
        self.codegen = EnhancedCodeGen(
            self.version_manager,
            self.decision_logger
        )
        self.validator = EnhancedValidator(
            self.version_manager,
            self.diff_engine
        )
        
        # Estado interno
        self.current_iteration = 0
        self.last_result: Optional[IterationResult] = None
    
    def run_iteration(
        self,
        requirements: str,
        iteration_number: int,
        user_feedback: Optional[str] = None,
        user_instructions: Optional[str] = None
    ) -> IterationResult:
        """
        Ejecuta una iteración completa del pipeline:
        1. Análisis arquitectural (con contexto histórico)
        2. Generación de código (con memoria de código previo)
        3. Validación (con análisis de tendencias)
        4. Guardar resultados
        
        Args:
            requirements: Requerimientos del sistema
            iteration_number: Número de iteración (1, 2, 3, ...)
            user_feedback: Feedback del usuario sobre iteración previa
            user_instructions: Instrucciones específicas para esta iteración
            
        Returns:
            IterationResult con todos los resultados de la iteración
        """
        print("=" * 80)
        print(f"🚀 ITERACIÓN {iteration_number} - {self.project_name}")
        print("=" * 80)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if user_feedback:
            print(f"Feedback: {user_feedback}")
        if user_instructions:
            print(f"Instrucciones: {user_instructions}")
        print("=" * 80)
        print()
        
        iteration_start = time.time()
        phase_durations = {}
        
        try:
            # FASE 1: Análisis arquitectural
            print("📊 FASE 1: Análisis Arquitectural")
            print("-" * 80)
            phase_start = time.time()
            
            analysis_result = self.analyzer.analyze(
                requirements=requirements,
                project_name=self.project_name,
                current_iteration=iteration_number,
                user_feedback=user_feedback
            )
            
            phase_durations['analyzer'] = time.time() - phase_start
            print(f"✅ Análisis completado en {phase_durations['analyzer']:.2f}s")
            print()
            
            # FASE 2: Generación de código
            print("💻 FASE 2: Generación de Código")
            print("-" * 80)
            phase_start = time.time()
            
            codegen_result = self.codegen.generate(
                analysis_result=analysis_result,
                project_name=self.project_name,
                current_iteration=iteration_number,
                user_instructions=user_instructions
            )
            
            phase_durations['codegen'] = time.time() - phase_start
            print(f"✅ Generación completada en {phase_durations['codegen']:.2f}s")
            print()
            
            # FASE 3: Validación
            print("🔍 FASE 3: Validación")
            print("-" * 80)
            phase_start = time.time()
            
            validation_result = self.validator.validate(
                codegen_result=codegen_result,
                analysis_result=analysis_result,
                project_name=self.project_name,
                current_iteration=iteration_number
            )
            
            phase_durations['validator'] = time.time() - phase_start
            print(f"✅ Validación completada en {phase_durations['validator']:.2f}s")
            print()
            
            # Construir resultado de iteración
            iteration_duration = time.time() - iteration_start
            
            result = IterationResult(
                iteration=iteration_number,
                project_name=self.project_name,
                analysis=analysis_result,
                codegen=codegen_result,
                validation=validation_result,
                timestamp=datetime.now(),
                duration_seconds=iteration_duration,
                phase_durations=phase_durations
            )
            
            # Guardar iteración completa
            self._save_iteration_results(result, requirements, user_feedback)
            
            # Actualizar estado interno
            self.current_iteration = iteration_number
            self.last_result = result
            
            # Mostrar resumen
            self._print_iteration_summary(result)
            
            return result
            
        except Exception as e:
            print()
            print("=" * 80)
            print(f"❌ ERROR EN ITERACIÓN {iteration_number}: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()
            raise
    
    def post_validation_menu(self, result: IterationResult) -> str:
        """
        Menú interactivo post-validación.
        Permite al usuario decidir qué hacer después de validar.
        
        Opciones:
        1. Aceptar y continuar (guarda y avanza)
        2. Regenerar código (mantiene arquitectura, regenera código con feedback)
        3. Rediseñar arquitectura (recomienza desde análisis)
        4. Ver detalles de validación
        5. Salir
        
        Args:
            result: Resultado de la iteración actual
            
        Returns:
            Opción elegida ('accept', 'regenerate', 'redesign', 'details', 'exit')
        """
        print()
        print("=" * 80)
        print("🛑 MENÚ POST-VALIDACIÓN")
        print("=" * 80)
        print()
        print(f"Iteración {result.iteration} completada.")
        print(f"Scores: {result.get_final_scores()}")
        print(f"Issues detectados: {result.get_issues_count()}")
        print()
        print("¿Qué deseas hacer?")
        print()
        print("  1. ✅ Aceptar y continuar")
        print("  2. 🔄 Regenerar código (con feedback específico)")
        print("  3. 🎨 Rediseñar arquitectura (cambio mayor)")
        print("  4. 📋 Ver detalles de validación")
        print("  5. 🚪 Salir")
        print()
        
        while True:
            try:
                choice = input("Elige una opción (1-5): ").strip()
                
                if choice == '1':
                    return 'accept'
                elif choice == '2':
                    return 'regenerate'
                elif choice == '3':
                    return 'redesign'
                elif choice == '4':
                    self._show_validation_details(result)
                    # Volver a mostrar el menú
                    continue
                elif choice == '5':
                    return 'exit'
                else:
                    print("❌ Opción inválida. Por favor elige 1-5.")
                    
            except KeyboardInterrupt:
                print()
                print("⚠️ Operación cancelada por el usuario")
                return 'exit'
    
    def regenerate_code(
        self,
        previous_result: IterationResult,
        user_feedback: str
    ) -> IterationResult:
        """
        Regenera solo el código manteniendo la arquitectura.
        Útil para ajustes pequeños sin cambiar el diseño arquitectural.
        
        Flujo:
        1. Reutiliza el análisis de la iteración anterior
        2. Ejecuta CodeGen con el feedback del usuario
        3. Ejecuta Validator
        4. Guarda como nueva iteración
        
        Args:
            previous_result: Resultado de la iteración anterior
            user_feedback: Feedback específico del usuario sobre qué mejorar
            
        Returns:
            IterationResult con código regenerado
        """
        print()
        print("=" * 80)
        print("🔄 REGENERANDO CÓDIGO")
        print("=" * 80)
        print(f"Manteniendo arquitectura de iteración {previous_result.iteration}")
        print(f"Feedback: {user_feedback}")
        print("=" * 80)
        print()
        
        new_iteration = previous_result.iteration + 1
        iteration_start = time.time()
        phase_durations = {}
        
        try:
            # Reutilizar análisis anterior (no regenerar)
            analysis_result = previous_result.analysis
            print("📊 Reutilizando análisis anterior")
            print()
            
            # Registrar decisión de regeneración
            self.decision_logger.log_decision(
                iteration=new_iteration,
                phase='orchestrator',
                decision=f'Regenerate code only (keep architecture)',
                rationale=f'User requested code regeneration: {user_feedback}',
                alternatives_considered=['Full redesign', 'Accept as-is'],
                chosen_alternative='Code regeneration',
                impacted_components=['codegen'],
                triggered_by='user_feedback'
            )
            
            # FASE 2: Regenerar código
            print("💻 FASE 2: Regeneración de Código")
            print("-" * 80)
            phase_start = time.time()
            
            codegen_result = self.codegen.generate(
                analysis_result=analysis_result,
                project_name=self.project_name,
                current_iteration=new_iteration,
                user_instructions=f"FEEDBACK FROM PREVIOUS ITERATION: {user_feedback}"
            )
            
            phase_durations['codegen'] = time.time() - phase_start
            print(f"✅ Regeneración completada en {phase_durations['codegen']:.2f}s")
            print()
            
            # FASE 3: Validación
            print("🔍 FASE 3: Validación")
            print("-" * 80)
            phase_start = time.time()
            
            validation_result = self.validator.validate(
                codegen_result=codegen_result,
                analysis_result=analysis_result,
                project_name=self.project_name,
                current_iteration=new_iteration
            )
            
            phase_durations['validator'] = time.time() - phase_start
            print(f"✅ Validación completada en {phase_durations['validator']:.2f}s")
            print()
            
            # Construir resultado
            iteration_duration = time.time() - iteration_start
            phase_durations['analyzer'] = 0.0  # No se ejecutó
            
            result = IterationResult(
                iteration=new_iteration,
                project_name=self.project_name,
                analysis=analysis_result,
                codegen=codegen_result,
                validation=validation_result,
                timestamp=datetime.now(),
                duration_seconds=iteration_duration,
                phase_durations=phase_durations
            )
            
            # Guardar iteración
            self._save_iteration_results(
                result,
                requirements=previous_result.analysis.get('requirements', 'N/A'),
                user_feedback=user_feedback
            )
            
            # Actualizar estado
            self.current_iteration = new_iteration
            self.last_result = result
            
            self._print_iteration_summary(result)
            
            return result
            
        except Exception as e:
            print()
            print(f"❌ ERROR EN REGENERACIÓN: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def redesign_architecture(
        self,
        previous_result: IterationResult,
        user_instructions: str
    ) -> IterationResult:
        """
        Rediseña la arquitectura completamente.
        Ejecuta una nueva iteración desde el análisis.
        
        Flujo:
        1. Ejecuta Analyzer con instrucciones del usuario
        2. Ejecuta CodeGen con nueva arquitectura
        3. Ejecuta Validator
        4. Guarda como nueva iteración
        
        Args:
            previous_result: Resultado de la iteración anterior
            user_instructions: Instrucciones del usuario para el rediseño
            
        Returns:
            IterationResult con arquitectura rediseñada
        """
        print()
        print("=" * 80)
        print("🎨 REDISEÑANDO ARQUITECTURA")
        print("=" * 80)
        print(f"Partiendo de iteración {previous_result.iteration}")
        print(f"Instrucciones: {user_instructions}")
        print("=" * 80)
        print()
        
        new_iteration = previous_result.iteration + 1
        
        # Registrar decisión de rediseño
        self.decision_logger.log_decision(
            iteration=new_iteration,
            phase='orchestrator',
            decision='Redesign architecture',
            rationale=f'User requested architectural redesign: {user_instructions}',
            alternatives_considered=['Keep current architecture', 'Minor adjustments'],
            chosen_alternative='Full redesign',
            impacted_components=['analyzer', 'codegen', 'validator'],
            triggered_by='user_instructions'
        )
        
        # Ejecutar iteración completa con feedback
        requirements = previous_result.analysis.get('requirements', 'N/A')
        
        return self.run_iteration(
            requirements=requirements,
            iteration_number=new_iteration,
            user_feedback=f"Architectural redesign requested: {user_instructions}",
            user_instructions=user_instructions
        )
    
    def accept_and_continue(self, result: IterationResult) -> None:
        """
        Acepta los resultados de la iteración actual.
        Guarda el estado y prepara para la siguiente iteración.
        
        Args:
            result: Resultado de la iteración actual
        """
        print()
        print("=" * 80)
        print("✅ ITERACIÓN ACEPTADA")
        print("=" * 80)
        print(f"Iteración {result.iteration} guardada exitosamente.")
        print(f"Proyecto: {self.project_name}")
        print()
        
        # Registrar decisión de aceptación
        self.decision_logger.log_decision(
            iteration=result.iteration,
            phase='orchestrator',
            decision='Accept iteration',
            rationale='User approved iteration results',
            alternatives_considered=['Regenerate', 'Redesign'],
            chosen_alternative='Accept',
            impacted_components=['all'],
            triggered_by='user_approval'
        )
        
        print("La iteración ha sido aceptada. Puedes continuar con la siguiente.")
        print()
    
    def _save_iteration_results(
        self,
        result: IterationResult,
        requirements: str,
        user_feedback: Optional[str] = None
    ) -> None:
        """
        Guarda los resultados de una iteración en el storage.
        
        Args:
            result: Resultado de la iteración
            requirements: Requerimientos originales
            user_feedback: Feedback del usuario (opcional)
        """
        # Crear ProjectState
        state = ProjectState(
            project_name=self.project_name,
            iteration=result.iteration,
            parent_iteration=result.iteration - 1 if result.iteration > 1 else None,
            created_at=result.timestamp,
            original_requirements=requirements,
            outputs={
                'analysis': result.analysis,
                'code_generation': result.codegen,
                'validation': result.validation
            },
            user_feedback=user_feedback,
            execution_metrics={
                'total_duration': result.duration_seconds,
                'phase_durations': result.phase_durations
            }
        )
        
        # Crear Iteration completa
        iteration = Iteration(
            project_name=self.project_name,
            iteration_number=result.iteration,
            state=state,
            decisions=[],  # Las decisiones ya se guardaron con DecisionLogger
            created_at=result.timestamp,
            duration_seconds=result.duration_seconds,
            phase_durations=result.phase_durations,
            final_scores=result.get_final_scores(),
            status='completed'
        )
        
        # Guardar con VersionManager
        self.storage.save_iteration(iteration)
        
        print(f"💾 Iteración {result.iteration} guardada exitosamente")
    
    def _print_iteration_summary(self, result: IterationResult) -> None:
        """Imprime resumen de la iteración"""
        print()
        print("=" * 80)
        print(f"📊 RESUMEN ITERACIÓN {result.iteration}")
        print("=" * 80)
        print()
        
        # Duración total
        print(f"⏱️  Duración total: {result.duration_seconds:.2f}s ({result.duration_seconds/60:.2f} min)")
        print()
        
        # Duración por fase
        print("📈 Tiempo por fase:")
        for phase, duration in result.phase_durations.items():
            print(f"   {phase:12s}: {duration:6.2f}s")
        print()
        
        # Scores finales
        scores = result.get_final_scores()
        if scores:
            print("🎯 Scores finales:")
            for metric, score in scores.items():
                print(f"   {metric:12s}: {score}/10")
            print()
        
        # Issues detectados
        if result.has_issues():
            print(f"⚠️  Issues detectados: {result.get_issues_count()}")
        else:
            print("✅ No se detectaron issues")
        
        print()
        print("=" * 80)
        print()
    
    def _show_validation_details(self, result: IterationResult) -> None:
        """Muestra detalles completos de la validación"""
        print()
        print("=" * 80)
        print("📋 DETALLES DE VALIDACIÓN")
        print("=" * 80)
        print()
        
        validation = result.validation
        
        # Scores
        if 'scores' in validation:
            print("🎯 Scores:")
            for metric, score in validation['scores'].items():
                print(f"   {metric}: {score}/10")
            print()
        
        # Issues
        if 'issues' in validation and validation['issues']:
            print(f"⚠️  Issues ({len(validation['issues'])}):")
            for i, issue in enumerate(validation['issues'], 1):
                severity = issue.get('severity', 'unknown')
                description = issue.get('description', 'No description')
                component = issue.get('component', 'N/A')
                print(f"   {i}. [{severity.upper()}] {description}")
                print(f"      Componente: {component}")
            print()
        else:
            print("✅ No se detectaron issues")
            print()
        
        # Análisis de tendencias (si existe)
        if 'trend_analysis' in validation and validation['trend_analysis']:
            trends = validation['trend_analysis']
            if isinstance(trends, dict) and 'summary' in trends:
                print(f"📈 Tendencias: {trends['summary']}")
                print()
        
        # Recomendaciones (si existen)
        if 'recommendations' in validation and validation['recommendations']:
            print("💡 Recomendaciones:")
            for i, rec in enumerate(validation['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()
        
        print("=" * 80)
        input("\nPresiona Enter para continuar...")
        print()


def create_iterative_orchestrator(
    project_name: str,
    storage
) -> IterativeOrchestrator:
    """
    Factory function para crear un IterativeOrchestrator.
    
    Args:
        project_name: Nombre del proyecto
        storage: Backend de almacenamiento
        
    Returns:
        IterativeOrchestrator configurado
    """
    return IterativeOrchestrator(project_name, storage)
    
