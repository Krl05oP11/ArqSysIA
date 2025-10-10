#!/usr/bin/env python3
"""
Test script para OutputGenerator

Genera documentos finales en markdown a partir de un ProjectState existente.
"""

import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from arqsysia.core.state import StateManager
from arqsysia.outputs.generator import create_generator


def main():
    """Ejecuta el test del Output Generator."""
    
    print("="*70)
    print("🧪 TEST DEL OUTPUT GENERATOR")
    print("="*70)
    print()
    
    # 1. Cargar estado existente
    print("1️⃣  Cargando estado del proyecto...")
    
    state_manager = StateManager()
    
    # Usar el proyecto TaskManager generado por el orchestrator
    project_name = "taskmanager"
    
    try:
        state = state_manager.load_state(project_name)
        print(f"✅ Estado cargado: {state.project_name}")
        print(f"   Outputs disponibles: {len(state.outputs)}")
        print()
    except FileNotFoundError:
        print(f"❌ Estado no encontrado: {project_name}")
        print("   Debes ejecutar primero test_orchestrator.py")
        print()
        
        # Listar estados disponibles
        output_dir = Path("output")
        if output_dir.exists():
            json_files = list(output_dir.glob("*_state.json"))
            if json_files:
                print("Estados disponibles:")
                for f in json_files:
                    name = f.stem.replace("_state", "")
                    print(f"   - {name}")
                print()
        
        return
    
    # 2. Crear generador
    print("2️⃣  Creando generador de documentos...")
    generator = create_generator()
    print("✅ Generador creado")
    print()
    
    # 3. Generar todos los documentos
    print("3️⃣  Generando documentos...")
    print()
    
    try:
        generated_docs = generator.generate_all(state)
        
        print()
        print("="*70)
        print("✅ DOCUMENTOS GENERADOS EXITOSAMENTE")
        print("="*70)
        print()
        
        # 4. Mostrar resumen
        print("📄 DOCUMENTOS CREADOS:")
        print()
        
        for doc_type, filepath in generated_docs.items():
            file_size = filepath.stat().st_size
            
            print(f"📝 {doc_type}:")
            print(f"   Ruta: {filepath}")
            print(f"   Tamaño: {file_size:,} bytes")
            
            # Contar líneas
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"   Líneas: {lines}")
            print()
        
        # 5. Preview de cada documento
        print("="*70)
        print("📖 PREVIEW DE DOCUMENTOS")
        print("="*70)
        print()
        
        for doc_type, filepath in generated_docs.items():
            print(f"--- {doc_type.upper()} ---")
            print()
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                preview_lines = lines[:20]  # Primeras 20 líneas
                
                for line in preview_lines:
                    print(line.rstrip())
                
                if len(lines) > 20:
                    print(f"\n... ({len(lines) - 20} líneas más)\n")
            
            print()
        
        # 6. Información adicional
        print("="*70)
        print("💡 INFORMACIÓN ADICIONAL")
        print("="*70)
        print()
        
        print("Para visualizar los documentos completos:")
        print()
        for doc_type, filepath in generated_docs.items():
            print(f"  cat {filepath}")
        print()
        
        print("O abre los archivos con tu editor favorito:")
        print()
        for doc_type, filepath in generated_docs.items():
            print(f"  nano {filepath}")
        print()
        
        # 7. Resumen de contenido
        print("="*70)
        print("📊 RESUMEN DE CONTENIDO")
        print("="*70)
        print()
        
        # MVP Proposal
        if "mvp_proposal" in generated_docs:
            mvp_path = generated_docs["mvp_proposal"]
            with open(mvp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("📝 Propuesta de MVP:")
            print(f"   Incluye: Requerimientos, Stack, Componentes, Roadmap")
            print(f"   Ideal para: Presentar a clientes y stakeholders")
            print()
        
        # Technical Architecture
        if "technical_architecture" in generated_docs:
            tech_path = generated_docs["technical_architecture"]
            with open(tech_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("🏗️  Arquitectura Técnica:")
            print(f"   Incluye: Patrón arquitectural, Stack detallado, Componentes")
            print(f"   Ideal para: Desarrolladores y equipos técnicos")
            print()
        
        # Validation Report
        if "validation_report" in generated_docs:
            val_path = generated_docs["validation_report"]
            with open(val_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("🔍 Reporte de Validación:")
            print(f"   Incluye: Scores, Vulnerabilidades, Recomendaciones")
            print(f"   Ideal para: QA, seguridad, y mejora continua")
            print()
        
        print("="*70)
        print("✨ Test completado exitosamente")
        print("="*70)
        print()
        
    except Exception as e:
        print()
        print("="*70)
        print(f"❌ ERROR AL GENERAR DOCUMENTOS: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
    
