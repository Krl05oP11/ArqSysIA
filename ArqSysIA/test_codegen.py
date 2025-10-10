#!/usr/bin/env python3
"""
Script de prueba para CodeGen (Fase 2)

Ejecuta el CodeGen sobre un análisis existente para verificar
que genera correctamente:
- Estructura de archivos
- Código de archivos clave
- Scripts de setup
- Documentación técnica
"""

import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from arqsysia.clients.ollama_client import OllamaClient
from arqsysia.core.state import ProjectState, StateManager
from arqsysia.phases.codegen import CodeGenPhase


def main():
    print("=" * 70)
    print("PRUEBA DE CODEGEN (FASE 2)")
    print("=" * 70)
    print()
    
    # 1. Cargar un análisis existente
    print("📂 Cargando análisis existente...")
    
    # Usar el análisis del blog personal que ya existe
    state_file = Path("test_output/blog_personal_state.json")
    
    if not state_file.exists():
        print(f"❌ No se encontró el archivo: {state_file}")
        print("⚠️  Primero ejecuta test_analyzer.py para crear el análisis")
        return 1
    
    # Cargar estado
    state_manager = StateManager(output_dir="test_output")
    state = state_manager.load_state("blog_personal")
    
    print(f"✅ Estado cargado: {state.project_name}")
    print(f"   - Fase 1 completa: {state.metadata.get('phase_1_complete', False)}")
    print()
    
    # 2. Verificar que el análisis está completo
    if not state.metadata.get("phase_1_complete"):
        print("❌ El análisis (Fase 1) no está completo")
        print("   Ejecuta primero test_analyzer.py")
        return 1
    
    # 3. Inicializar cliente Ollama
    print("🔧 Inicializando cliente Ollama...")
    client = OllamaClient()
    
    # Verificar modelo
    if not client.check_model_available("deepseek-r1:32b"):
        print("❌ Modelo deepseek-r1:32b no disponible")
        print("   Ejecuta: ollama pull deepseek-r1:32b")
        return 1
    
    print("✅ Cliente Ollama listo")
    print()
    
    # 4. Ejecutar CodeGen
    print("🚀 Ejecutando CodeGen (Fase 2)...")
    print("   ⚠️  Esto puede tomar 10-20 minutos (generación de código)")
    print()
    
    codegen = CodeGenPhase(
        ollama_client=client,
        model_name="qwen2.5-coder:32b-instruct"
    )
    
    try:
        # Ejecutar fase
        state = codegen.run(state)
        
        print()
        print("=" * 70)
        print("✅ CODEGEN COMPLETADO")
        print("=" * 70)
        print()
        
        # 5. Mostrar resultados
        print_results(state)
        
        # 6. Guardar estado actualizado
        print("\n💾 Guardando estado...")
        state_manager.save_state(state, format="json")
        state_manager.save_state(state, format="yaml")
        
        print(f"✅ Estado guardado en test_output/")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error ejecutando CodeGen: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_results(state: ProjectState):
    """Imprime los resultados del CodeGen."""
    
    # Estructura de archivos
    print("📁 ESTRUCTURA DE ARCHIVOS")
    print("-" * 70)
    file_structure = state.get_output("file_structure")
    if file_structure:
        print(f"   Raíz: {list(file_structure.get('root', {}).get('children', {}).keys())[:10]}")
        print(f"   Total nodos: {count_nodes(file_structure)}")
    else:
        print("   ⚠️  No se generó estructura")
    print()
    
    # Archivos generados
    print("📄 ARCHIVOS GENERADOS")
    print("-" * 70)
    generated_files = state.get_output("generated_files")
    if generated_files:
        print(f"   Total archivos: {len(generated_files)}")
        for filename in list(generated_files.keys())[:5]:
            lines = generated_files[filename].count('\n') + 1
            print(f"   - {filename} ({lines} líneas)")
        if len(generated_files) > 5:
            print(f"   ... y {len(generated_files) - 5} archivos más")
    else:
        print("   ⚠️  No se generaron archivos")
    print()
    
    # Scripts de setup
    print("⚙️  SCRIPTS DE SETUP")
    print("-" * 70)
    setup_scripts = state.get_output("setup_scripts")
    if setup_scripts:
        print(f"   Total scripts: {len(setup_scripts)}")
        for script in setup_scripts[:3]:
            print(f"   - {script.get('name', 'N/A')}: {script.get('description', 'N/A')}")
        if len(setup_scripts) > 3:
            print(f"   ... y {len(setup_scripts) - 3} scripts más")
    else:
        print("   ⚠️  No se generaron scripts")
    print()
    
    # Documentación técnica
    print("📚 DOCUMENTACIÓN TÉCNICA")
    print("-" * 70)
    tech_docs = state.get_output("technical_documentation")
    if tech_docs:
        print(f"   Total documentos: {len(tech_docs)}")
        for doc_name in tech_docs.keys():
            lines = tech_docs[doc_name].count('\n') + 1
            print(f"   - {doc_name} ({lines} líneas)")
    else:
        print("   ⚠️  No se generó documentación")
    print()
    
    # Metadata
    print("📊 METADATA")
    print("-" * 70)
    print(f"   Fase 2 completa: {state.metadata.get('phase_2_complete', False)}")
    print(f"   Duración: {state.metadata.get('phase_2_duration', 'N/A')}")
    print()


def count_nodes(structure: dict, node: dict = None) -> int:
    """Cuenta recursivamente el número de nodos en la estructura."""
    if node is None:
        node = structure.get("root", {})
    
    count = 1  # Nodo actual
    
    children = node.get("children", {})
    for child in children.values():
        count += count_nodes(structure, child)
    
    return count


if __name__ == "__main__":
    sys.exit(main())
