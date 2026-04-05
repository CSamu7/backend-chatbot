#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'chatbot')

from ML.search import extraer_criterios_avanzados

print("="*60)
print("PRUEBA DE FUNCIÓN: extraer_criterios_avanzados()")
print("="*60)

# Prueba 1: Búsqueda simple de género
resultado1 = extraer_criterios_avanzados('Busco libros de fantasía')
print('\n✓ Prueba 1 - "Busco libros de fantasía":')
print(f"  Resultado: {resultado1}")
print(f"  Géneros detectados: {resultado1.get('generos', [])}")

# Prueba 2: Con páginas y género
resultado2 = extraer_criterios_avanzados('Busco libros de terror de menos de 300 páginas')
print('\n✓ Prueba 2 - "Busco libros de terror de menos de 300 páginas":')
print(f"  Resultado: {resultado2}")
print(f"  Géneros: {resultado2.get('generos', [])}")
print(f"  Max páginas: {resultado2.get('max_paginas', 'N/A')}")

# Prueba 3: Búsqueda avanzada con área
resultado3 = extraer_criterios_avanzados('Busco literatura americana de ciencia ficción')
print('\n✓ Prueba 3 - "Busco literatura americana de ciencia ficción":')
print(f"  Resultado: {resultado3}")
print(f"  Géneros: {resultado3.get('generos', [])}")
print(f"  Área: {resultado3.get('area', 'N/A')}")

# Prueba 4: Espacios en blanco
resultado4 = extraer_criterios_avanzados('Busco libros de Fantasía ')
print('\n✓ Prueba 4 - "Busco libros de Fantasía " (con espacio):')
print(f"  Resultado: {resultado4}")
print(f"  Géneros detectados: {resultado4.get('generos', [])}")

print("\n" + "="*60)
print("PRUEBAS COMPLETADAS")
print("="*60)
