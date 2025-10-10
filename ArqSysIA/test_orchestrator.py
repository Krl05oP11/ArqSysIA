#!/usr/bin/env python3
"""
Test script para PipelineOrchestrator

Prueba la ejecución completa del pipeline:
1. Analyzer → 2. CodeGen → 3. Validator

Modos:
- Interactivo: Solicita aprobación entre fases
- Automático: Ejecuta todo sin interrupciones
"""

import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from arqsysia.core.orchestrator import create_orchestrator


# Requerimientos de ejemplo - Sistema de gestión de tareas
REQUIREMENTS = """
# Sistema de Gestión de Tareas para Equipos

## Descripción
Aplicación web para gestión de tareas y proyectos de equipos pequeños (5-20 personas).

## Funcionalidades Principales
1. Gestión de usuarios (registro, login, perfiles)
2. Creación y edición de proyectos
3. Gestión de tareas dentro de proyectos:
   - Crear, editar, eliminar tareas
   - Asignar responsables
   - Establecer fechas límite
   - Agregar comentarios
   - Adjuntar archivos
4. Estados de tareas: Por hacer, En progreso, Completada
5. Tablero Kanban por proyecto
6. Dashboard con resumen de actividades
7. Notificaciones por email
8. Búsqueda de tareas

## Requerimientos No Funcionales
- Debe soportar hasta 50 usuarios concurrentes
- Interfaz responsive (mobile-first)
- Tiempo de respuesta < 2 segundos
- Disponibilidad 99%
- Datos encriptados en tránsito y reposo
- Backup diario automático
- Fácil despliegue (Docker)

## Usuarios
- Administrador: Gestiona usuarios y proyectos
- Manager: Crea proyectos y asigna tareas
- Miembro: Trabaja en tareas asignadas

## Stack Preferido (sugerencia)
- Backend: Python/Node.js
- Frontend: React/Vue
- Base de datos: PostgreSQL
- Priorizar tecnologías open-source
"""


def main():
    """Ejecuta el test del orchestrator."""
    
    print("="*70)
    print("🧪 TEST DEL PIPELINE ORCHESTRATOR")
    print("="*70)
    print()
    
    # Solicitar modo de ejecución
    print("Modos de ejecución:")
    print("  1. Automático (sin checkpoints, más rápido)")
    print("  2. Interactivo (solicita aprobación entre fases)")
    print()
    
    while True:
        mode = input("Selecciona modo (1/2): ").strip()
        if mode in ['1', '2']:
            break
        print("⚠️  Opción inválida. Por favor selecciona 1 o 2.")
    
    interactive = mode == '2'
    print()
    
    if interactive:
        print("🛑 Modo INTERACTIVO activado")
        print("   Se solicitará aprobación después de cada fase")
    else:
        print("⚡ Modo AUTOMÁTICO activado")
        print("   El pipeline se ejecutará sin interrupciones")
    
    print()
    
    # Crear orchestrator
    print("1️⃣  Creando orchestrator...")
    orchestrator = create_orchestrator(interactive=interactive)
    print("✅ Orchestrator creado")
    print()
    
    # Definir proyecto
    project_name = "TaskManager"
    
    print(f"2️⃣  Proyecto: {project_name}")
    print(f"   Requerimientos: {len(REQUIREMENTS)} caracteres")
    print()
    
    # Preguntar si desea ejecutar
    if interactive:
        response = input("¿Iniciar pipeline? (s/n): ").strip().lower()
        if response not in ['s', 'si', 'yes', 'y']:
            print("\n❌ Ejecución cancelada")
            return
        print()
    
    # Ejecutar pipeline
    print("3️⃣  Ejecutando pipeline completo...")
    print()
    
    try:
        state = orchestrator.run(
            requirements=REQUIREMENTS,
            project_name=project_name
        )
        
        print()
        print("="*70)
        print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        print("="*70)
        print()
        
        # Mostrar métricas
        metrics = orchestrator.get_metrics()
        
        print("📊 MÉTRICAS DETALLADAS:")
        print()
        print(f"   Total de fases completadas: {len(metrics['phases_completed'])}")
        print(f"   Fases: {', '.join(metrics['phases_completed'])}")
        print()
        
        print("⏱️  TIEMPOS:")
        for phase, duration in metrics['phase_durations'].items():
            print(f"   {phase:12s}: {duration:6.1f}s ({duration/60:5.1f} min)")
        print(f"   {'TOTAL':12s}: {metrics['total_duration']:6.1f}s ({metrics['total_duration']/60:5.1f} min)")
        print()
        
        # Información del estado
        print("📁 ESTADO DEL PROYECTO:")
        print(f"   Nombre: {state.project_name}")
        print(f"   Outputs generados: {len(state.outputs)}")
        print(f"   Archivo: output/{state.project_name.lower()}_state.json")
        print()
        
        # Resumen de validación (si existe)
        validation_results = state.get_output("validation_results")
        if validation_results:
            print("📈 SCORES DE VALIDACIÓN:")
            
            if "architecture" in validation_results:
                arch = validation_results["architecture"]
                print(f"   📐 Arquitectura: {arch.get('architecture_score', 0)}/10")
                print(f"      Inconsistencias: {len(arch.get('inconsistencies', []))}")
                print(f"      Mejoras sugeridas: {len(arch.get('improvements', []))}")
            
            if "code" in validation_results:
                code = validation_results["code"]
                print(f"   💻 Código: {code.get('code_quality_score', 0)}/10")
                print(f"      Errores potenciales: {len(code.get('potential_errors', []))}")
                print(f"      Code smells: {len(code.get('code_smells', []))}")
            
            if "security" in validation_results:
                sec = validation_results["security"]
                print(f"   🔒 Seguridad: {sec.get('security_score', 0)}/10")
                print(f"      Vulnerabilidades: {len(sec.get('vulnerabilities', []))}")
                print(f"      Recomendaciones: {len(sec.get('priority_recommendations', []))}")
            
            print()
        
        print("="*70)
        print("✨ Test completado exitosamente")
        print("📄 Revisa los resultados en output/")
        print("="*70)
        print()
        
    except KeyboardInterrupt:
        print()
        print()
        print("="*70)
        print("⚠️  PIPELINE INTERRUMPIDO POR EL USUARIO")
        print("="*70)
        print()
        print("💾 Estado parcial guardado en output/")
        print()
        sys.exit(1)
        
    except Exception as e:
        print()
        print()
        print("="*70)
        print(f"❌ ERROR EN PIPELINE: {e}")
        print("="*70)
        print()
        import traceback
        traceback.print_exc()
        print()
        print("💾 Estado parcial guardado en output/")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
    
