#!/usr/bin/env python3
"""
ArqSysIA - Architecture Consultant Script
Consulta con DeepSeek-R1-32B sobre el diseño de ArqSysIA
"""

import json
import time
from datetime import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    print("ERROR: Biblioteca 'ollama' no encontrada.")
    print("Instalar con: pip install ollama")
    exit(1)


class ArchitectureConsultant:
    """Consultor de arquitectura usando DeepSeek-R1-32B"""
    
    def __init__(self, model: str = "deepseek-r1:32b"):
        self.model = model
        self.client = ollama.Client()
        
    def verify_model(self) -> bool:
        """Verifica que el modelo esté disponible"""
        try:
            # Listar modelos desde Ollama
            models_response = self.client.list()
            
            # Extraer lista de modelos
            # La respuesta es un objeto ListResponse con atributo 'models'
            if hasattr(models_response, 'models'):
                models_list = models_response.models
            elif isinstance(models_response, dict) and 'models' in models_response:
                models_list = models_response['models']
            elif isinstance(models_response, list):
                models_list = models_response
            else:
                print(f"❌ Estructura de respuesta inesperada: {type(models_response)}")
                return False
            
            # Extraer nombres de modelos
            available = []
            for m in models_list:
                # El objeto Model tiene atributo 'model' con el nombre
                if hasattr(m, 'model'):
                    available.append(m.model)
                elif hasattr(m, 'name'):
                    available.append(m.name)
                elif isinstance(m, dict):
                    name = m.get('model') or m.get('name')
                    if name:
                        available.append(name)
                elif isinstance(m, str):
                    available.append(m)
            
            if not available:
                print("❌ No se encontraron modelos instalados.")
                print("💡 Verifica con: ollama list")
                return False
            
            print(f"📦 Modelos disponibles: {len(available)} modelos encontrados")
            
            # Verificar si nuestro modelo está disponible
            if self.model not in available:
                print(f"❌ Modelo '{self.model}' no encontrado.")
                print(f"💡 Modelos disponibles que coinciden con 'deepseek-r1':")
                matching = [m for m in available if 'deepseek-r1' in m.lower()]
                for m in matching:
                    print(f"   - {m}")
                return False
            
            print(f"✅ Modelo '{self.model}' verificado.")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando con Ollama: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            print("💡 Asegúrate de que Ollama esté corriendo:")
            print("   ollama serve")
            return False
    
    def consult(self, question: str, context: str = "") -> dict:
        """Realiza una consulta al modelo"""
        
        prompt = f"""Eres un arquitecto de software experto especializado en sistemas con Inteligencia Artificial.

CONTEXTO:
{context}

PREGUNTA:
{question}

Por favor, proporciona un análisis detallado y profesional. Estructura tu respuesta con:
1. Evaluación de la decisión/diseño propuesto
2. Fortalezas del enfoque
3. Posibles debilidades o riesgos
4. Recomendaciones específicas y accionables
5. Consideraciones de implementación

Sé directo, preciso y justifica tus recomendaciones."""

        print(f"\n🤔 Consultando con {self.model}...")
        print(f"   Pregunta: {question[:100]}...")
        
        start_time = time.time()
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 4096,
                }
            )
            
            elapsed = time.time() - start_time
            
            return {
                'success': True,
                'question': question,
                'response': response['message']['content'],
                'model': self.model,
                'elapsed_seconds': elapsed,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            }


def load_foundational_document() -> str:
    """Carga el documento fundacional como contexto"""
    # Lista de posibles ubicaciones y nombres
    possible_paths = [
        Path("arqsysia-foundational-doc.md"),  # ← Nombre real del archivo
        Path("ArqSysIA - Foundational Document.md"),
        Path("FOUNDATIONAL_DOCUMENT.md"),
        Path("foundational_document.md"),
        Path("docs/arqsysia-foundational-doc.md"),
        Path("docs/ArqSysIA - Foundational Document.md"),
    ]
    
    # Intentar encontrar el archivo
    for doc_path in possible_paths:
        if doc_path.exists():
            print(f"✅ Documento fundacional encontrado: {doc_path}")
            try:
                content = doc_path.read_text(encoding='utf-8')
                print(f"   Contexto cargado: {len(content)} caracteres")
                return content
            except Exception as e:
                print(f"⚠️  Error leyendo archivo: {e}")
                continue
    
    # Si no se encuentra, listar archivos .md disponibles
    print("⚠️  Documento fundacional no encontrado.")
    print("📂 Archivos .md encontrados en el directorio actual:")
    md_files = list(Path(".").glob("*.md"))
    if md_files:
        for f in md_files:
            print(f"   - {f.name}")
    else:
        print("   (ninguno)")
    
    print("\n💡 Continuando sin contexto del documento fundacional.")
    print("   Las respuestas serán más genéricas sin este contexto.\n")
    
    return ""


def main():
    """Ejecuta la consultoría arquitectural"""
    
    print("=" * 70)
    print("  ArqSysIA - Consultoría Arquitectural con DeepSeek-R1-32B")
    print("=" * 70)
    
    # Inicializar consultor
    consultant = ArchitectureConsultant()
    
    # Verificar que el modelo esté disponible
    if not consultant.verify_model():
        return
    
    # Cargar contexto
    print("\n📄 Cargando documento fundacional...")
    context = load_foundational_document()
    
    if context:
        print(f"   Contexto cargado: {len(context)} caracteres")
    
    # Preguntas de consultoría
    consultations = [
        {
            "id": "1_architecture_pattern",
            "question": """¿Es correcta la decisión de usar un pipeline tradicional orquestado 
            en lugar de un sistema multi-agente para ArqSysIA? Considera:
            - El flujo lineal: Análisis → Generación → Validación
            - Usuario individual (no equipo)
            - Necesidad de control explícito y checkpoints manuales
            - Principio de simplicidad sobre complejidad
            
            ¿Cuál sería tu recomendación?"""
        },
        {
            "id": "2_model_selection",
            "question": """¿Es apropiada la selección de 3 modelos especializados para ArqSysIA?
            - DeepSeek-R1-32B para análisis (razonamiento profundo)
            - Qwen2.5-Coder-32B para generación de código
            - DeepSeek-R1-14B para validación (más rápido)
            
            ¿Hay alguna consideración que no hayamos contemplado? 
            ¿Debería usarse un solo modelo para todo o el enfoque multi-modelo es correcto?"""
        },
        {
            "id": "3_infrastructure",
            "question": """¿Es óptima la arquitectura híbrida propuesta?
            - Aplicación en Docker
            - Ollama corriendo en host (localhost:11434)
            - No duplicar modelos (ahorro de espacio)
            
            ¿Hay algún riesgo o limitación importante en este enfoque?
            ¿Cuándo sería necesario migrar a vLLM u otra solución?"""
        },
        {
            "id": "4_iterative_workflow",
            "question": """Para el flujo de trabajo iterativo/cíclico de ArqSysIA:
            - Usuario ingresa requerimientos → ArqSysIA genera código
            - Usuario encuentra errores → vuelve a ingresar correcciones
            - ArqSysIA refina el código generado
            
            ¿Necesitamos implementar RAG (Retrieval Augmented Generation) con vector database
            para mantener contexto entre iteraciones, o es suficiente con:
            - Mantener estado del proyecto en archivos JSON/YAML
            - Cargar código previo en context window del LLM (128k tokens)
            
            ¿Cuál es tu recomendación para el MVP y para la versión final?"""
        }
    ]
    
    # Realizar consultas
    results = []
    
    for i, consultation in enumerate(consultations, 1):
        print(f"\n{'=' * 70}")
        print(f"  Consulta {i}/{len(consultations)}: {consultation['id']}")
        print(f"{'=' * 70}")
        
        result = consultant.consult(
            question=consultation['question'],
            context=context
        )
        
        if result['success']:
            print(f"\n✅ Respuesta recibida ({result['elapsed_seconds']:.1f}s)")
            print(f"\n{'-' * 70}")
            print(result['response'])
            print(f"{'-' * 70}")
        else:
            print(f"\n❌ Error: {result['error']}")
        
        results.append(result)
        
        # Pausa entre consultas
        if i < len(consultations):
            print("\n⏳ Esperando 2 segundos antes de la siguiente consulta...")
            time.sleep(2)
    
    # Guardar resultados
    output_path = Path("consultant_report.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 70}")
    print(f"✅ Consultoría completada!")
    print(f"📄 Reporte guardado en: {output_path}")
    print(f"{'=' * 70}")
    
    # Resumen
    successful = sum(1 for r in results if r['success'])
    total_time = sum(r.get('elapsed_seconds', 0) for r in results)
    
    print(f"\n📊 Resumen:")
    print(f"   Consultas exitosas: {successful}/{len(consultations)}")
    print(f"   Tiempo total: {total_time:.1f}s")
    print(f"\n💡 Próximo paso: Revisa 'consultant_report.json' y ajusta el diseño si es necesario.")


if __name__ == "__main__":
    main()
