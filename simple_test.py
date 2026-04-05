import sys
import os
sys.path.append('chatbot')

from ML.core import predict_intent

# Prueba simple
questions = [
    "que generos tienes",
    "que generos hay",
    "fantasia"
]

for q in questions:
    intent = predict_intent(q, {})
    print(f"'{q}' -> {intent}")
    print(f"'{q}' -> {intent}")