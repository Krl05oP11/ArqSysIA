#!/usr/bin/env python3
"""
Script de prueba para OllamaClient.

Verifica:
1. Conectividad con Ollama
2. Modelos disponibles
3. Generación básica con DeepSeek-R1-32B
"""

import sys
from pathlib import Path

# El script está en ~/Projects/ArqSysIA/
# El código está en ~/Projects/ArqSysIA/arqsysia/
# Python ya puede importar directamente

from arqsysia.clients import create_client, OllamaClientError


def main():
    print("=" * 60)
    print("🧪 ArqSysIA - Test de OllamaClient")
    print("=" * 60)
    print()
    
    # 1. Crear cliente
    print("1️⃣  Creando cliente Ollama...")
    try:
        client = create_client()
        print("   ✅ Cliente creado")
    except Exception as e:
        print(f"   ❌ Error creando cliente: {e}")
        return 1
    
    # 2. Verificar conectividad
    print("\n2️⃣  Verificando conectividad con Ollama...")
    if client.ping():
        print("   ✅ Ollama está accesible")
    else:
        print("   ❌ No se puede conectar a Ollama")
        print("   💡 Asegúrate de que Ollama esté corriendo:")
        print("      ollama serve")
        return 1
    
    # 3. Listar modelos
    print("\n3️⃣  Listando modelos disponibles...")
    try:
        models = client.list_models()
        print(f"   ✅ {len(models)} modelos encontrados:")
        for model in models:
            print(f"      • {model}")
    except OllamaClientError as e:
        print(f"   ❌ Error listando modelos: {e}")
        return 1
    
    # 4. Verificar DeepSeek-R1-32B
    print("\n4️⃣  Verificando DeepSeek-R1-32B...")
    target_model = "deepseek-r1:32b"
    if client.check_model_available(target_model):
        print(f"   ✅ {target_model} está disponible")
    else:
        print(f"   ⚠️  {target_model} NO está disponible")
        print(f"   💡 Descárgalo con: ollama pull {target_model}")
        # No retornamos error, seguimos con el test
    
    # 5. Test de generación simple
    print("\n5️⃣  Test de generación simple...")
    test_prompt = "Di 'Hola desde ArqSysIA' en una sola línea."
    
    try:
        print(f"   Enviando prompt: '{test_prompt}'")
        print("   ⏳ Generando respuesta...")
        
        response = client.generate(
            model=target_model,
            prompt=test_prompt,
            temperature=0.3
        )
        
        print("\n   ✅ Respuesta recibida:")
        print("   " + "─" * 56)
        print(f"   {response}")
        print("   " + "─" * 56)
        
    except OllamaClientError as e:
        print(f"   ❌ Error en generación: {e}")
        return 1
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return 1
    
    # 6. Test de streaming (opcional)
    print("\n6️⃣  Test de streaming (opcional)...")
    print("   Generando con streaming...")
    
    try:
        stream = client.generate(
            model=target_model,
            prompt="Cuenta del 1 al 5, un número por línea.",
            temperature=0.3,
            stream=True
        )
        
        print("   📡 Stream: ", end="", flush=True)
        for chunk in stream:
            print(chunk, end="", flush=True)
        print()  # Nueva línea al final
        print("   ✅ Streaming completado")
        
    except Exception as e:
        print(f"   ⚠️  Streaming no disponible: {e}")
        # No es error crítico
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ Todos los tests completados exitosamente")
    print("=" * 60)
    print()
    print("💡 Próximo paso: Implementar State Manager")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
