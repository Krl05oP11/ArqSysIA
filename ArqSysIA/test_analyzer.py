#!/usr/bin/env python3
"""
Script de prueba para Analyzer (Fase 1)

Ejecuta el análisis arquitectural sobre un conjunto de requerimientos
para verificar que el Analyzer funciona correctamente.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from arqsysia.clients.ollama_client import OllamaClient
from arqsysia.core.state import ProjectState, StateManager
from arqsysia.phases.analyzer import AnalyzerPhase


def main():
    print("=" * 70)
    print("PRUEBA DE ANALYZER (FASE 1)")
    print("=" * 70)
    print()
    
    # 1. Definir requerimientos de prueba
    project_name = "blog_personal"
    requirements = """
    Desarrollar un blog personal para un desarrollador de software que incluya:
    
    Funcionalidades:
    - Sistema de autenticación para el autor
    - Editor de posts con markdown
    - Categorías y etiquetas
    - Comentarios (opcional para MVP)
    - Búsqueda de posts
    - RSS feed
    - Responsive design
    
    Restricciones:
    - Debe ser fácil de desplegar
    - Bajo costo de mantenimiento
    - Buen rendimiento SEO
    - El autor es desarrollador individual (no equipo)
    """
    
    print(f"📋 Proyecto: {project_name}")
    print(f"📝 Requerimientos: {len(requirements)} caracteres")
    print()
    
    # 2. Inicializar cliente Ollama
    print("🔧 Inicializando cliente Ollama...")
    client = OllamaClient()
    
    # Verificar que el modelo esté disponible
    model_name = "deepseek-r1:32b"
    if not client.check_model_available(model_name):
        print(f"❌ Modelo {model_name} no disponible")
        print(f"   Ejecuta: ollama pull {model_name}")
        return 1
    
    print(f"✅ Cliente Ollama listo (modelo: {model_name})")
    print()
    
    # 3. Crear estado inicial
    print("📦 Creando estado inicial del proyecto...")
    state = ProjectState(
        project_name=project_name,
        original_requirements=requirements,
    )
    print("✅ Estado inicial creado")
    print()
    
    # 4. Ejecutar Analyzer
    print("🚀 Ejecutando Analyzer (Fase 1)...")
    print("   ⚠️  Esto puede tomar 4-5 minutos (análisis profundo)")
    print()
    
    analyzer = AnalyzerPhase(
        ollama_client=client,
        model_name=model_name
    )
    
    try:
        # Ejecutar análisis
        state = analyzer.run(state)
        
        print()
        print("=" * 70)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 70)
        print()
        
        # 5. Mostrar resultados
        print_analysis_results(state)
        
        # 6. Guardar estado
        print("\n💾 Guardando estado...")
        state_manager = StateManager(output_dir="test_output")
        state_manager.save_state(state, format="json")
        state_manager.save_state(state, format="yaml")
        
        print(f"✅ Estado guardado en test_output/")
        print(f"   - {project_name}_state.json")
        print(f"   - {project_name}_state.yaml")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error ejecutando Analyzer: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_analysis_results(state: ProjectState):
    """Imprime los resultados del análisis de forma legible."""
    
    analysis = state.get_output("analysis")
    
    if not analysis:
        print("⚠️  No se encontró análisis en el estado")
        return
    
    # Requerimientos funcionales
    print("📋 REQUERIMIENTOS FUNCIONALES")
    print("-" * 70)
    func_reqs = analysis.get("functional_requirements", [])
    for i, req in enumerate(func_reqs[:5], 1):
        print(f"   {i}. {req}")
    if len(func_reqs) > 5:
        print(f"   ... y {len(func_reqs) - 5} más")
    print()
    
    # Requerimientos no funcionales
    print("⚙️  REQUERIMIENTOS NO FUNCIONALES")
    print("-" * 70)
    non_func_reqs = analysis.get("non_functional_requirements", [])
    for i, req in enumerate(non_func_reqs[:5], 1):
        print(f"   {i}. {req}")
    if len(non_func_reqs) > 5:
        print(f"   ... y {len(non_func_reqs) - 5} más")
    print()
    
    # Arquitectura
    print("🏗️  ARQUITECTURA")
    print("-" * 70)
    print(f"   Patrón: {analysis.get('architecture_pattern', 'N/A')}")
    justification = analysis.get('architecture_justification', 'N/A')
    print(f"   Justificación: {justification[:100]}...")
    print()
    
    # Stack tecnológico
    print("💻 STACK TECNOLÓGICO")
    print("-" * 70)
    tech_stack = analysis.get('tech_stack', {})
    for category, tech in tech_stack.items():
        print(f"   {category}: {tech}")
    print()
    
    # Componentes principales
    print("🔧 COMPONENTES PRINCIPALES")
    print("-" * 70)
    components = analysis.get('main_components', [])
    for i, comp in enumerate(components[:5], 1):
        if isinstance(comp, dict):
            name = comp.get('name', 'N/A')
            desc = comp.get('description', 'N/A')
            print(f"   {i}. {name}: {desc[:60]}...")
        else:
            print(f"   {i}. {comp}")
    if len(components) > 5:
        print(f"   ... y {len(components) - 5} más")
    print()
    
    # MVP Scope
    print("🎯 ALCANCE MVP")
    print("-" * 70)
    mvp_scope = analysis.get('mvp_scope', [])
    for i, feature in enumerate(mvp_scope[:5], 1):
        print(f"   {i}. {feature}")
    if len(mvp_scope) > 5:
        print(f"   ... y {len(mvp_scope) - 5} más")
    print()
    
    # Roadmap
    print("🗺️  ROADMAP")
    print("-" * 70)
    roadmap = analysis.get('roadmap', [])
    for i, phase in enumerate(roadmap[:3], 1):
        if isinstance(phase, dict):
            name = phase.get('phase', f'Fase {i}')
            desc = phase.get('description', 'N/A')
            print(f"   {name}: {desc[:60]}...")
        else:
            print(f"   Fase {i}: {phase}")
    if len(roadmap) > 3:
        print(f"   ... y {len(roadmap) - 3} fases más")
    print()
    
    # Metadata
    print("📊 METADATA")
    print("-" * 70)
    print(f"   Fase 1 completa: {state.metadata.get('phase_1_complete', False)}")
    print(f"   Duración análisis: {state.metadata.get('phase_1_duration', 'N/A')}")
    print()


if __name__ == "__main__":
    sys.exit(main())
    
