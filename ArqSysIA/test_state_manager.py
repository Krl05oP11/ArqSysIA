#!/usr/bin/env python3
"""
Script de prueba para StateManager.

Verifica:
1. Creación de ProjectState
2. Actualización de fases
3. Guardado/carga (JSON y YAML)
4. StateManager completo
"""

from pathlib import Path
from arqsysia.core import (
    ProjectState,
    StateManager,
    PipelinePhase,
    PhaseResult,
    AnalysisResult,
    GenerationResult,
    ValidationResult,
)


def main():
    print("=" * 60)
    print("🧪 ArqSysIA - Test de StateManager")
    print("=" * 60)
    print()
    
    # 1. Crear StateManager
    print("1️⃣  Creando StateManager...")
    output_dir = Path("./test_output")
    manager = StateManager(output_dir=output_dir)
    print(f"   ✅ StateManager creado (output: {output_dir})")
    
    # 2. Crear proyecto
    print("\n2️⃣  Creando proyecto de prueba...")
    requirements = """
    Sistema de gestión de tareas con:
    - Autenticación de usuarios
    - CRUD de tareas
    - Asignación de tareas a usuarios
    - Notificaciones en tiempo real
    """
    
    state = manager.create_project(
        project_name="task_manager",
        requirements=requirements,
        model_config={
            "analysis": "deepseek-r1:32b",
            "generation": "deepseek-r1:32b",
            "validation": "deepseek-r1:32b"
        }
    )
    print(f"   ✅ Proyecto creado: {state.project_name}")
    print(f"   📅 Creado: {state.created_at}")
    
    # 3. Simular Fase 1: Análisis
    print("\n3️⃣  Simulando Fase 1 - Análisis...")
    state.update_phase(PipelinePhase.ANALYZING)
    
    analysis = AnalysisResult(
        functional_requirements=[
            "Registro e inicio de sesión de usuarios",
            "Crear, leer, actualizar y eliminar tareas",
            "Asignar tareas a usuarios específicos"
        ],
        non_functional_requirements=[
            "Rendimiento: < 200ms respuesta",
            "Seguridad: Autenticación JWT",
            "Escalabilidad: Soportar 1000 usuarios concurrentes"
        ],
        architecture_pattern="MVC (Model-View-Controller)",
        architecture_justification="Separación clara de responsabilidades",
        tech_stack={
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "frontend": "React",
            "realtime": "WebSockets"
        },
        main_components=[
            "API REST",
            "Gestor de autenticación",
            "Módulo de tareas",
            "Sistema de notificaciones"
        ],
        mvp_scope="Autenticación + CRUD de tareas",
        product_roadmap="MVP → Notificaciones → Colaboración"
    )
    
    state.set_analysis_result(analysis)
    state.add_phase_result(PhaseResult(
        phase="analysis",
        status="completed",
        duration_seconds=45.2,
        model_used="deepseek-r1:32b"
    ))
    state.update_phase(PipelinePhase.ANALYSIS_COMPLETE)
    
    print("   ✅ Análisis completado")
    print(f"   🏗️  Arquitectura: {analysis.architecture_pattern}")
    print(f"   ⚙️  Backend: {analysis.tech_stack.get('backend')}")
    
    # 4. Simular Fase 2: Generación
    print("\n4️⃣  Simulando Fase 2 - Generación...")
    state.update_phase(PipelinePhase.GENERATING)
    
    generation = GenerationResult(
        generated_files=[
            "app/main.py",
            "app/models/task.py",
            "app/routes/auth.py"
        ],
        setup_scripts=[
            "setup.sh",
            "docker-compose.yml"
        ],
        documentation_files=[
            "README.md",
            "API_DOCS.md"
        ]
    )
    
    state.set_generation_result(generation)
    state.add_phase_result(PhaseResult(
        phase="generation",
        status="completed",
        duration_seconds=30.5,
        model_used="deepseek-r1:32b"
    ))
    state.update_phase(PipelinePhase.GENERATION_COMPLETE)
    
    print("   ✅ Generación completada")
    print(f"   📄 Archivos generados: {len(generation.generated_files)}")
    
    # 5. Simular Fase 3: Validación
    print("\n5️⃣  Simulando Fase 3 - Validación...")
    state.update_phase(PipelinePhase.VALIDATING)
    
    validation = ValidationResult(
        inconsistencies=[
            "Falta definir índices en base de datos"
        ],
        potential_errors=[
            "No hay manejo de rate limiting"
        ],
        suggested_improvements=[
            "Agregar cache con Redis",
            "Implementar logging estructurado"
        ],
        security_considerations=[
            "Validar inputs en todos los endpoints",
            "Implementar CORS correctamente"
        ]
    )
    
    state.set_validation_result(validation)
    state.add_phase_result(PhaseResult(
        phase="validation",
        status="completed",
        duration_seconds=20.1,
        model_used="deepseek-r1:32b"
    ))
    state.update_phase(PipelinePhase.VALIDATION_COMPLETE)
    
    print("   ✅ Validación completada")
    print(f"   ⚠️  Sugerencias: {len(validation.suggested_improvements)}")
    
    # 6. Guardar estado (JSON)
    print("\n6️⃣  Guardando estado como JSON...")
    json_path = manager.save_state(format="json")
    print(f"   ✅ Guardado: {json_path}")
    print(f"   📦 Tamaño: {json_path.stat().st_size} bytes")
    
    # 7. Guardar estado (YAML)
    print("\n7️⃣  Guardando estado como YAML...")
    yaml_path = manager.save_state(format="yaml")
    print(f"   ✅ Guardado: {yaml_path}")
    print(f"   📦 Tamaño: {yaml_path.stat().st_size} bytes")
    
    # 8. Cargar estado desde JSON
    print("\n8️⃣  Cargando estado desde JSON...")
    loaded_state = manager.load_state(json_path)
    print(f"   ✅ Estado cargado")
    print(f"   📛 Proyecto: {loaded_state.project_name}")
    print(f"   🔄 Fase actual: {loaded_state.current_phase}")
    print(f"   ✅ Análisis presente: {loaded_state.analysis is not None}")
    print(f"   ✅ Generación presente: {loaded_state.generation is not None}")
    print(f"   ✅ Validación presente: {loaded_state.validation is not None}")
    
    # 9. Verificar datos cargados
    print("\n9️⃣  Verificando integridad de datos...")
    assert loaded_state.project_name == "task_manager"
    assert loaded_state.current_phase == PipelinePhase.VALIDATION_COMPLETE.value
    assert loaded_state.analysis.architecture_pattern == "MVC (Model-View-Controller)"
    assert len(loaded_state.phase_results) == 3
    print("   ✅ Todos los datos se cargaron correctamente")
    
    # 10. Resumen
    print("\n" + "=" * 60)
    print("✅ Todos los tests del StateManager completados")
    print("=" * 60)
    print()
    print("📊 Resumen del Estado:")
    print(f"   • Proyecto: {loaded_state.project_name}")
    print(f"   • Fase: {loaded_state.current_phase}")
    print(f"   • Fases completadas: {len(loaded_state.phase_results)}")
    print(f"   • Tech Stack: {', '.join(loaded_state.analysis.tech_stack.values())}")
    print(f"   • Archivos generados: {len(loaded_state.generation.generated_files)}")
    print(f"   • Mejoras sugeridas: {len(loaded_state.validation.suggested_improvements)}")
    print()
    print("💡 Próximo paso: Implementar Phases (Analyzer, CodeGen, Validator)")
    print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
    
