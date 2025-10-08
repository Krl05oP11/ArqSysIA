#!/usr/bin/env python3
"""
Script de prueba para AnalyzerPhase (Fase 1).

Prueba el análisis arquitectural completo con DeepSeek-R1-32B.
"""

from pathlib import Path
from arqsysia.clients import create_client
from arqsysia.phases import create_analyzer
from arqsysia.core import StateManager, PipelinePhase


def main():
    print("=" * 70)
    print("🧪 ArqSysIA - Test de Analyzer (Fase 1)")
    print("=" * 70)
    print()
    
    # 1. Crear cliente Ollama
    print("1️⃣  Creando cliente Ollama...")
    try:
        client = create_client()
        if not client.ping():
            print("   ❌ No se puede conectar a Ollama")
            return 1
        print("   ✅ Cliente Ollama conectado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1
    
    # 2. Crear Analyzer
    print("\n2️⃣  Creando Analyzer...")
    model = "deepseek-r1:32b"
    try:
        analyzer = create_analyzer(client, model=model, verbose=True)
        print(f"   ✅ Analyzer creado (modelo: {model})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1
    
    # 3. Preparar requerimientos de prueba
    print("\n3️⃣  Preparando requerimientos de prueba...")
    requirements = """
Sistema de Blog Personal con las siguientes características:

FUNCIONALIDAD:
- Los usuarios deben poder crear, editar y eliminar artículos
- Soporte para categorías y etiquetas en los artículos
- Sistema de comentarios en los artículos
- Búsqueda de artículos por título, contenido, categorías o etiquetas
- Editor de texto enriquecido (rich text editor)
- Subida de imágenes para los artículos
- Vista previa antes de publicar
- Borradores (guardar sin publicar)

USUARIOS:
- Sistema de autenticación (registro, login, logout)
- Roles: Admin (gestión total) y Autor (solo sus artículos)
- Perfil de usuario con avatar

RENDIMIENTO:
- El sitio debe cargar en menos de 2 segundos
- Debe soportar al menos 100 lectores concurrentes
- Las búsquedas deben ser rápidas (< 500ms)

TECNOLOGÍA:
- Preferir tecnologías modernas y open-source
- El sitio debe ser responsive (mobile-friendly)
- SEO-friendly (URLs amigables, meta tags)

DESPLIEGUE:
- Debe ser fácil de desplegar
- Preferiblemente con Docker
"""
    
    print(f"   ✅ Requerimientos preparados ({len(requirements)} caracteres)")
    print("\n   📋 Requerimientos:")
    print("   " + "-" * 66)
    for line in requirements.strip().split('\n')[:10]:
        print(f"   {line}")
    print("   ...")
    print("   " + "-" * 66)
    
    # 4. Ejecutar análisis
    print("\n4️⃣  Ejecutando análisis arquitectural...")
    print("   ⏳ Esto puede tomar 1-3 minutos con DeepSeek-R1-32B...")
    print()
    
    try:
        result = analyzer.run(requirements)
        
        if result.status == "failed":
            print(f"\n   ❌ Análisis falló: {result.error}")
            return 1
        
        print(f"\n   ✅ Análisis completado en {result.duration_seconds:.2f} segundos")
        
    except Exception as e:
        print(f"\n   ❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 5. Mostrar resultados
    print("\n5️⃣  Resultados del análisis:")
    print("   " + "=" * 66)
    
    output = result.output
    
    # Requerimientos funcionales
    print("\n   📌 REQUERIMIENTOS FUNCIONALES:")
    for i, req in enumerate(output.get('functional_requirements', [])[:5], 1):
        print(f"      {i}. {req}")
    if len(output.get('functional_requirements', [])) > 5:
        print(f"      ... y {len(output['functional_requirements']) - 5} más")
    
    # Requerimientos no funcionales
    print("\n   ⚙️  REQUERIMIENTOS NO FUNCIONALES:")
    for i, req in enumerate(output.get('non_functional_requirements', [])[:5], 1):
        print(f"      {i}. {req}")
    
    # Arquitectura
    print("\n   🏗️  ARQUITECTURA:")
    print(f"      Patrón: {output.get('architecture_pattern', 'N/A')}")
    justification = output.get('architecture_justification', 'N/A')
    print(f"      Justificación: {justification[:100]}...")
    
    # Stack tecnológico
    print("\n   💻 TECH STACK:")
    for key, value in output.get('tech_stack', {}).items():
        print(f"      • {key.capitalize()}: {value}")
    
    # Componentes principales
    print("\n   🧩 COMPONENTES PRINCIPALES:")
    for i, comp in enumerate(output.get('main_components', [])[:5], 1):
        print(f"      {i}. {comp}")
    
    # MVP Scope
    print("\n   🎯 MVP SCOPE:")
    mvp = output.get('mvp_scope', 'N/A')
    print(f"      {mvp[:200]}...")
    
    # Roadmap
    print("\n   🗺️  PRODUCT ROADMAP:")
    roadmap = output.get('product_roadmap', 'N/A')
    print(f"      {roadmap[:200]}...")
    
    print("\n   " + "=" * 66)
    
    # 6. Integrar con StateManager
    print("\n6️⃣  Guardando estado del proyecto...")
    
    try:
        state_manager = StateManager(output_dir=Path("./test_output"))
        state = state_manager.create_project(
            project_name="blog_personal",
            requirements=requirements,
            model_config={"analysis": model}
        )
        
        # Actualizar estado con resultado de análisis
        state.update_phase(PipelinePhase.ANALYZING)
        
        # Convertir a AnalysisResult
        analysis_result = analyzer.to_analysis_result(output)
        state.set_analysis_result(analysis_result)
        
        # Agregar resultado de fase
        state.add_phase_result(result)
        state.update_phase(PipelinePhase.ANALYSIS_COMPLETE)
        
        # Guardar
        saved_path = state_manager.save_state(format="json")
        print(f"   ✅ Estado guardado: {saved_path}")
        
        # También guardar YAML para inspección
        yaml_path = state_manager.save_state(format="yaml")
        print(f"   ✅ Estado guardado: {yaml_path}")
        
    except Exception as e:
        print(f"   ⚠️  No se pudo guardar estado: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ Test de Analyzer completado exitosamente")
    print("=" * 70)
    print()
    print("📊 RESUMEN:")
    print(f"   • Tiempo de análisis: {result.duration_seconds:.2f}s")
    print(f"   • Modelo usado: {result.model_used}")
    print(f"   • Reqs funcionales: {len(output.get('functional_requirements', []))}")
    print(f"   • Reqs no funcionales: {len(output.get('non_functional_requirements', []))}")
    print(f"   • Arquitectura: {output.get('architecture_pattern', 'N/A')}")
    print(f"   • Componentes: {len(output.get('main_components', []))}")
    print()
    print("💡 Los resultados completos están en:")
    print(f"   • test_output/blog_personal_state.json")
    print(f"   • test_output/blog_personal_state.yaml")
    print()
    print("🚀 Próximo paso: Implementar Fase 2 (CodeGen)")
    print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
