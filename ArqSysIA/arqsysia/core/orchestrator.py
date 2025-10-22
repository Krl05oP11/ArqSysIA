"""
Pipeline Orchestrator - Coordinador Principal de ArqSysIA

Coordina la ejecución secuencial de las 3 fases:
1. Analyzer - Análisis de arquitectura
2. CodeGen - Generación de código
3. Validator - Validación

Características:
- Checkpoints entre fases (aprobación manual opcional)
- Manejo global de errores
- Métricas de tiempo por fase
- Estado persistente después de cada fase
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime

from arqsysia.clients.ollama_client import OllamaClient
from arqsysia.core.state import ProjectState
from arqsysia.phases.analyzer import AnalyzerPhase
from arqsysia.phases.codegen import CodeGenPhase
from arqsysia.phases.validator import ValidatorPhase


class PipelineOrchestrator:
    """
    Coordina la ejecución del pipeline completo de ArqSysIA.
    """
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        #state_manager: Optional[StateManager] = None,
        interactive: bool = True
    ):
        """
        Inicializa el orquestador del pipeline.
        
        Args:
            ollama_client: Cliente de Ollama configurado
            state_manager: Gestor de estado (si es None, crea uno nuevo)
            interactive: Si True, solicita aprobación entre fases
        """
        self.ollama_client = ollama_client
        #self.state_manager = state_manager or StateManager()
        self.interactive = interactive
        
        # Métricas
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "phase_durations": {},
            "phases_completed": []
        }
        
        # Inicializar fases
        self.analyzer = AnalyzerPhase(
            ollama_client=ollama_client,
            model_name="deepseek-r1:32b"
        )
        
        self.codegen = CodeGenPhase(
            ollama_client=ollama_client,
            model_name="qwen2.5-coder:32b-instruct"
        )
        
        self.validator = ValidatorPhase(
            ollama_client=ollama_client,
            model_name="deepseek-r1:14b"
        )
    
    def run(
        self,
        requirements: str,
        project_name: str,
        skip_phases: Optional[list] = None
    ) -> ProjectState:
        """
        Ejecuta el pipeline completo.
        
        Args:
            requirements: Requerimientos del proyecto
            project_name: Nombre del proyecto
            skip_phases: Lista de fases a saltar (ej: ["validator"])
            
        Returns:
            ProjectState con todos los resultados
        """
        skip_phases = skip_phases or []
        
        print("="*70)
        print("🚀 ARQSYSIA - PIPELINE DE ARQUITECTURA DE SOFTWARE")
        print("="*70)
        print(f"Proyecto: {project_name}")
        print(f"Modo: {'Interactivo' if self.interactive else 'Automático'}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print()
        
        self.metrics["start_time"] = time.time()
        
        # Crear estado inicial
        state = ProjectState(
            project_name=project_name,
            original_requirements=requirements
        )
        
        try:
            # FASE 1: Analyzer
            if "analyzer" not in skip_phases:
                state = self._run_phase(
                    phase_name="Analyzer",
                    phase_number=1,
                    phase_instance=self.analyzer,
                    state=state
                )
                
                if self.interactive and not self._checkpoint("Analyzer"):
                    print("\n⚠️  Pipeline cancelado por el usuario")
                    return state
            else:
                print("⏭️  Fase Analyzer saltada")
                print()
            
            # FASE 2: CodeGen
            if "codegen" not in skip_phases:
                state = self._run_phase(
                    phase_name="CodeGen",
                    phase_number=2,
                    phase_instance=self.codegen,
                    state=state
                )
                
                if self.interactive and not self._checkpoint("CodeGen"):
                    print("\n⚠️  Pipeline cancelado por el usuario")
                    return state
            else:
                print("⏭️  Fase CodeGen saltada")
                print()
            
            # FASE 3: Validator
            if "validator" not in skip_phases:
                state = self._run_phase(
                    phase_name="Validator",
                    phase_number=3,
                    phase_instance=self.validator,
                    state=state
                )
            else:
                print("⏭️  Fase Validator saltada")
                print()
            
            # Pipeline completado
            self.metrics["end_time"] = time.time()
            self.metrics["total_duration"] = self.metrics["end_time"] - self.metrics["start_time"]
            
            self._print_final_summary(state)
            
            return state
            
        except Exception as e:
            print()
            print("="*70)
            print(f"❌ ERROR EN PIPELINE: {e}")
            print("="*70)
            import traceback
            traceback.print_exc()
            
            # Guardar estado parcial
            print("\n💾 Guardando estado parcial...")
            self.state_manager.save_state(state)
            print("✅ Estado parcial guardado")
            
            raise
    
    def _run_phase(
        self,
        phase_name: str,
        phase_number: int,
        phase_instance,
        state: ProjectState
    ) -> ProjectState:
        """
        Ejecuta una fase individual del pipeline.
        
        Args:
            phase_name: Nombre de la fase
            phase_number: Número de la fase (1, 2, 3)
            phase_instance: Instancia de la fase a ejecutar
            state: Estado actual del proyecto
            
        Returns:
            ProjectState actualizado
        """
        print(f"{'='*70}")
        print(f"📍 FASE {phase_number}: {phase_name.upper()}")
        print(f"{'='*70}")
        print()
        
        phase_start = time.time()
        
        try:
            # Ejecutar fase
            state = phase_instance.run(state)
            
            phase_end = time.time()
            phase_duration = phase_end - phase_start
            
            # Registrar métricas
            self.metrics["phase_durations"][phase_name] = phase_duration
            self.metrics["phases_completed"].append(phase_name)
            
            print()
            print(f"✅ {phase_name} completado en {phase_duration:.1f}s ({phase_duration/60:.1f} min)")
            print()
            
            # Guardar estado después de cada fase
            print(f"💾 Guardando estado después de {phase_name}...")
            self.state_manager.save_state(state)
            print(f"✅ Estado guardado")
            print()
            
            return state
            
        except Exception as e:
            print()
            print(f"❌ Error en fase {phase_name}: {e}")
            raise
    
    def _checkpoint(self, phase_name: str) -> bool:
        """
        Checkpoint entre fases para aprobación manual.
        
        Args:
            phase_name: Nombre de la fase completada
            
        Returns:
            True si el usuario aprueba continuar, False si cancela
        """
        print("="*70)
        print(f"🛑 CHECKPOINT: {phase_name} completado")
        print("="*70)
        print()
        print(f"La fase {phase_name} se ha completado exitosamente.")
        print("Puedes revisar los resultados antes de continuar.")
        print()
        
        while True:
            response = input("¿Continuar con la siguiente fase? (s/n): ").strip().lower()
            
            if response in ['s', 'si', 'yes', 'y']:
                print()
                print("✅ Continuando con el pipeline...")
                print()
                return True
            elif response in ['n', 'no']:
                print()
                print("❌ Pipeline cancelado por el usuario")
                return False
            else:
                print("⚠️  Respuesta inválida. Por favor responde 's' o 'n'")
    
    def _print_final_summary(self, state: ProjectState) -> None:
        """Imprime resumen final del pipeline."""
        
        print("="*70)
        print("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
        print("="*70)
        print()
        
        print("📊 RESUMEN DE EJECUCIÓN:")
        print()
        
        # Tiempos por fase
        print("⏱️  Tiempo por fase:")
        for phase_name, duration in self.metrics["phase_durations"].items():
            print(f"   {phase_name:12s}: {duration:6.1f}s ({duration/60:5.1f} min)")
        
        print()
        print(f"   {'TOTAL':12s}: {self.metrics['total_duration']:6.1f}s ({self.metrics['total_duration']/60:5.1f} min)")
        print()
        
        # Scores (si hay validación)
        validation_results = state.get_output("validation_results")
        if validation_results:
            print("📈 SCORES DE VALIDACIÓN:")
            
            if "architecture" in validation_results:
                arch_score = validation_results["architecture"].get("architecture_score", 0)
                print(f"   📐 Arquitectura: {arch_score}/10")
            
            if "code" in validation_results:
                code_score = validation_results["code"].get("code_quality_score", 0)
                print(f"   💻 Código:       {code_score}/10")
            
            if "security" in validation_results:
                sec_score = validation_results["security"].get("security_score", 0)
                print(f"   🔒 Seguridad:    {sec_score}/10")
            
            print()
        
        # Outputs generados
        print("📁 OUTPUTS GENERADOS:")
        print(f"   Estado del proyecto: output/{state.project_name.lower().replace(' ', '_')}_state.json")
        
        outputs = state.outputs
        if outputs:
            print(f"   Total de outputs: {len(outputs)}")
            print()
        
        print("="*70)
        print()
        print("✨ Proyecto analizado y validado exitosamente")
        print("📄 Puedes revisar los resultados en el directorio output/")
        print()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de ejecución del pipeline.
        
        Returns:
            Dict con métricas de tiempo y fases completadas
        """
        return self.metrics.copy()


def create_orchestrator(
    interactive: bool = True
) -> PipelineOrchestrator:
    """
    Factory function para crear un orchestrator con configuración por defecto.
    
    Args:
        interactive: Si True, solicita aprobación entre fases
        
    Returns:
        PipelineOrchestrator configurado
    """
    ollama_client = OllamaClient()
    #state_manager = StateManager()
    
    return PipelineOrchestrator(
        ollama_client=ollama_client,
        state_manager=state_manager,
        interactive=interactive
    )
    
