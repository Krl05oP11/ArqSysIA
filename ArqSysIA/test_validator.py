#!/usr/bin/env python3
"""
Test script para ValidatorPhase (Fase 3)

Prueba la validación de arquitectura y código generado.
Usa un estado previamente generado por Analyzer y CodeGen.
"""

import sys
import time
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from arqsysia.clients.ollama_client import OllamaClient
from arqsysia.core.state import StateManager
from arqsysia.phases.validator import ValidatorPhase


def main():
    """Ejecuta el test del Validator."""
    
    print("="*70)
    print("🧪 TEST DEL VALIDATOR (FASE 3)")
    print("="*70)
    print()
    
    # 1. Configurar cliente Ollama
    print("1️⃣  Configurando cliente Ollama...")
    client = OllamaClient()
    
    # Verificar modelo
    model_name = "deepseek-r1:14b"
    models = client.list_models()
    if model_name not in models:
        print(f"❌ Modelo {model_name} no encontrado")
        print(f"Modelos disponibles: {models}")
        print(f"\nPara descargar: ollama pull {model_name}")
        return
    
    print(f"✅ Modelo {model_name} disponible")
    print()
    
    # 2. Cargar estado existente (debe tener Analyzer y CodeGen)
    print("2️⃣  Cargando estado del proyecto...")
    
    state_manager = StateManager()
    state = state_manager.load_state("blog_personal")
    
    print(f"✅ Estado cargado: {state.project_name}")
    
    # Verificar que tenga resultados previos (compatible con versiones anteriores)
    has_analysis = (
        state.get_output("analysis_complete") or 
        state.get_output("analysis") is not None or
        state.get_output("architecture_analysis") is not None
    )
    
    has_codegen = (
        state.get_output("codegen_complete") or 
        state.get_output("file_structure") is not None or
        state.get_output("generated_files") is not None
    )
    
    print(f"   Analyzer completado: {'✅' if has_analysis else '❌'}")
    print(f"   CodeGen completado: {'✅' if has_codegen else '❌'}")
    
    if not has_analysis:
        print("\n❌ Debe ejecutarse Analyzer primero")
        print("   (o el estado no tiene datos de análisis)")
        return
    
    print()
    
    # 3. Ejecutar Validator
    print("3️⃣  Ejecutando Validator...")
    print()
    
    validator = ValidatorPhase(
        ollama_client=client,
        model_name=model_name
    )
    
    start_time = time.time()
    
    try:
        state = validator.run(state)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print()
        print("="*70)
        print(f"✅ VALIDATOR COMPLETADO EN {duration:.1f} SEGUNDOS ({duration/60:.1f} min)")
        print("="*70)
        print()
        
        # 4. Mostrar resultados
        print("4️⃣  Resultados de la validación:")
        print()
        
        validation_results = state.get_output("validation_results", {})
        
        # Arquitectura
        if "architecture" in validation_results:
            arch = validation_results["architecture"]
            print("📐 ARQUITECTURA:")
            print(f"   Score: {arch.get('architecture_score', 0)}/10")
            print(f"   Inconsistencias: {len(arch.get('inconsistencies', []))}")
            print(f"   Errores de diseño: {len(arch.get('design_errors', []))}")
            print(f"   Componentes faltantes: {len(arch.get('missing_components', []))}")
            print(f"   Mejoras: {len(arch.get('improvements', []))}")
            print()
        
        # Código
        if "code" in validation_results:
            code = validation_results["code"]
            print("💻 CÓDIGO:")
            print(f"   Score: {code.get('code_quality_score', 0)}/10")
            print(f"   Errores potenciales: {len(code.get('potential_errors', []))}")
            print(f"   Code smells: {len(code.get('code_smells', []))}")
            print(f"   Problemas estructura: {len(code.get('structure_issues', []))}")
            print(f"   Mejoras calidad: {len(code.get('quality_improvements', []))}")
            print()
        
        # Seguridad
        if "security" in validation_results:
            sec = validation_results["security"]
            print("🔒 SEGURIDAD:")
            print(f"   Score: {sec.get('security_score', 0)}/10")
            print(f"   Vulnerabilidades: {len(sec.get('vulnerabilities', []))}")
            print(f"   Prácticas faltantes: {len(sec.get('missing_practices', []))}")
            print(f"   Riesgos de datos: {len(sec.get('data_risks', []))}")
            print(f"   Recomendaciones: {len(sec.get('priority_recommendations', []))}")
            print()
        
        # Optimizaciones
        if "optimizations" in validation_results:
            opt = validation_results["optimizations"]
            print("⚡ OPTIMIZACIONES:")
            print(f"   Performance: {len(opt.get('performance', []))}")
            print(f"   Escalabilidad: {len(opt.get('scalability', []))}")
            print(f"   Mantenibilidad: {len(opt.get('maintainability', []))}")
            print(f"   Reducción costos: {len(opt.get('cost_reduction', []))}")
            print(f"   Prioridades: {len(opt.get('priority_optimizations', []))}")
            print()
        
        # Reporte
        report = state.get_output("validation_report", "")
        if report:
            print("📄 REPORTE GENERADO:")
            print(f"   {len(report)} caracteres")
            print()
            # Mostrar primeras líneas
            lines = report.split('\n')
            for line in lines[:15]:
                print(f"   {line}")
            if len(lines) > 15:
                print(f"   ... ({len(lines) - 15} líneas más)")
            print()
        
        # 5. Guardar estado actualizado
        print("5️⃣  Guardando estado actualizado...")
        
        # El StateManager guarda automáticamente en output/
        state_manager.save_state(state)
        
        print(f"✅ Estado guardado en output/")
        print()
        
        # 6. Resumen final
        print("="*70)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*70)
        print()
        print("📊 RESUMEN:")
        print(f"   ⏱️  Tiempo total: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"   📐 Score arquitectura: {validation_results.get('architecture', {}).get('architecture_score', 0)}/10")
        if "code" in validation_results:
            print(f"   💻 Score código: {validation_results.get('code', {}).get('code_quality_score', 0)}/10")
        print(f"   🔒 Score seguridad: {validation_results.get('security', {}).get('security_score', 0)}/10")
        print()
        print("📁 Estado completo guardado en output/")
        print()
        
    except Exception as e:
        print()
        print("="*70)
        print(f"❌ ERROR EN VALIDATOR: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
    
