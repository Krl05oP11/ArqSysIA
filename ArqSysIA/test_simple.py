#!/usr/bin/env python3
import ollama

print("Testing Ollama connection...")

try:
    # Test 1: Listar modelos
    client = ollama.Client(host='http://localhost:11434')
    response = client.list()
    
    print(f"Tipo de respuesta: {type(response)}")
    print(f"Keys: {response.keys() if isinstance(response, dict) else 'No es dict'}")
    
    models = response['models'] if isinstance(response, dict) else response.models
    print(f"✅ Conectado! {len(models)} modelos encontrados")
    
    # Test 2: Mostrar modelos (manejar objetos o dicts)
    for model in models[:3]:  # Solo primeros 3
        print(f"  Tipo de modelo: {type(model)}")
        if isinstance(model, dict):
            print(f"  • {model['name']}")
        else:
            # Es un objeto
            print(f"  • {model.name if hasattr(model, 'name') else model}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e)}")
    import traceback
    traceback.print_exc()
