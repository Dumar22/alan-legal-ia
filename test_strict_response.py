#!/usr/bin/env python3
"""
Test script para verificar que las respuestas estrictas funcionan correctamente
"""

def test_responses():
    """Casos de prueba para verificar respuestas estrictas"""
    
    print("🔬 PRUEBAS DE RESPUESTAS ESTRICTAS")
    print("=" * 50)
    
    # Casos de prueba
    test_cases = [
        {
            "query": "¿Qué dice sobre contratos?",
            "context": "Los contratos deben estar firmados por ambas partes según el artículo 15.",
            "expected": "Debería encontrar información sobre contratos y artículo 15"
        },
        {
            "query": "¿Cuál es el plazo para apelar?",
            "context": "El documento habla sobre procedimientos civiles pero no menciona plazos de apelación.",
            "expected": "Debería responder que no encuentra información sobre plazos de apelación"
        },
        {
            "query": "¿Qué dice sobre impuestos?",
            "context": "Este documento trata únicamente sobre contratos laborales y no contiene información fiscal.",
            "expected": "Debería responder que no encuentra información sobre impuestos"
        }
    ]
    
    print("📋 CASOS DE PRUEBA DEFINIDOS:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Query: {case['query']}")
        print(f"   Context: {case['context'][:100]}...")
        print(f"   Expected: {case['expected']}")
    
    print("\n✅ Script listo - ejecutar la aplicación y probar manualmente")
    print("💡 Mensaje esperado cuando no hay información:")
    print("   'La respuesta específica a esta pregunta no se encuentra en los documentos legales cargados'")
    
    # Verificar que el modelo actualizado esté en main.py
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'gpt-4o' in content and 'gpt-4o-mini' not in content:
                print("\n✅ Modelo actualizado correctamente a GPT-4o")
            elif 'gpt-4o-mini' in content:
                print("\n⚠️  Advertencia: Aún hay referencias a gpt-4o-mini")
            else:
                print("\n❌ No se detecta configuración de modelo")
                
        if 'La respuesta específica a esta pregunta no se encuentra en los documentos legales cargados' in content:
            print("✅ Mensaje de respuesta estricta configurado correctamente")
        else:
            print("⚠️  Advertencia: Mensaje de respuesta estricta podría no estar configurado")
            
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")

if __name__ == "__main__":
    test_responses()