#!/usr/bin/env python
"""
Cliente interactivo para probar el chatbot
Ejecuta: python chatbot_client.py
"""

import requests
import sys
import json

API_URL = "http://localhost:8000/api/chatbot/"

print("=" * 60)
print("CLIENTE INTERACTIVO - CHATBOT")
print("=" * 60)
print("Escribe 'salir' para terminar")
print("=" * 60)

while True:
    try:
        user_input = input("\nTú: ").strip()
        
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("\nBookbot: ¡Hasta luego!")
            break
        
        if not user_input:
            continue
        
        # Enviar al API
        response = requests.post(
            API_URL,
            json={"query": user_input},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print(f"\nBookbot: {data['response']}")
                # Mostrar info adicional si existe
                if "intent" in data:
                    print(f"[Intent detectado: {data['intent']}]")
            else:
                print(f"Error: {data}")
        else:
            print(f"Error del servidor: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. ¿Está corriendo Docker?")
        print(f"   Verificar: docker-compose ps")
        break
    except KeyboardInterrupt:
        print("\n\nBookbot: ¡Hasta luego!")
        break
    except Exception as e:
        print(f"Error: {e}")

print("=" * 60)
