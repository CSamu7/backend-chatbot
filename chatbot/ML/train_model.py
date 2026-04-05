"""
Script para entrenar el modelo del chatbot localmente sin Docker.
Ejecutar: python train_model.py
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Datos de entrenamiento
training_data = [
    # Saludos
    ("hola", "saludo"),
    ("buenos días", "saludo"),
    ("buenas tardes", "saludo"),
    ("buenas noches", "saludo"),
    ("qué tal", "saludo"),
    ("hey", "saludo"),
    ("saludos", "saludo"),
    
    # Buscar por título
    ("busco el libro Cien años de soledad", "buscar_titulo"),
    ("conoce el libro 1984", "buscar_titulo"),
    ("tienes el libro Don Quijote", "buscar_titulo"),
    ("libro llamado Rayuela", "buscar_titulo"),
    ("buscar libro Harry Potter", "buscar_titulo"),
    ("libro titulado Orgullo y prejuicio", "buscar_titulo"),
    ("quiero encontrar el libro La sombra del viento", "buscar_titulo"),
    
    # Buscar por autor
    ("libros de Gabriel García Márquez", "buscar_autor"),
    ("libros del autor Mario Vargas Llosa", "buscar_autor"),
    ("libro escrito por Isabel Allende", "buscar_autor"),
    ("autor Stephen King", "buscar_autor"),
    ("escritor Julio Cortázar", "buscar_autor"),
    ("obras de Pablo Neruda", "buscar_autor"),
    ("qué libros tienes de Jorge Luis Borges", "buscar_autor"),
    
    # Buscar por género
    ("libros de género romance", "buscar_genero"),
    ("género ciencia ficción", "buscar_genero"),
    ("tipo de libro misterio", "buscar_genero"),
    ("categoría fantasía", "buscar_genero"),
    ("novelas de terror", "buscar_genero"),
    ("libros de tipo histórico", "buscar_genero"),
    ("quiero libros de drama", "buscar_genero"),
    ("género policial", "buscar_genero"),
    
    # Buscar por área
    ("libros de área matemáticas", "buscar_area"),
    ("área de historia", "buscar_area"),
    ("materia filosofía", "buscar_area"),
    ("campo de estudio ciencia", "buscar_area"),
    ("temática tecnología", "buscar_area"),
    ("libros de área literatura", "buscar_area"),
    
    # Recomendaciones
    ("recomiéndame algo", "recomendacion"),
    ("qué me recomiendas", "recomendacion"),
    ("alguna recomendación", "recomendacion"),
    ("recomendación de libros", "recomendacion"),
    ("sugiéreme un libro", "recomendacion"),
    
    # Despedidas
    ("adiós", "despedida"),
    ("hasta luego", "despedida"),
    ("nos vemos", "despedida"),
    ("chao", "despedida"),
    ("bye", "despedida"),
    ("hasta pronto", "despedida"),
    
    # Conversación casual
    ("cómo estás", "estado_bot"),
    ("qué haces", "estado_bot"),
    ("cuéntame de ti", "presentacion"),
    ("quién eres", "presentacion"),
    ("de qué puedes hablar", "capacidades"),
    ("qué sabes hacer", "capacidades"),
    
    # Preguntas sobre el sistema
    ("cuántos libros tienes", "estadisticas"),
    ("qué géneros disponibles", "generos_disponibles"),
    ("qué géneros tienes", "generos_disponibles"),
    ("qué tipos de libros", "generos_disponibles"),
    ("qué categorías", "generos_disponibles"),
    ("qué géneros hay", "generos_disponibles"),
    ("muéstrame los géneros", "generos_disponibles"),
    ("dime los géneros", "generos_disponibles"),
    ("cuáles son los géneros", "generos_disponibles"),
    ("autores populares", "autores_populares"),
    ("libros recomendados", "recomendacion"),
    
    # Seguimiento de conversación
    ("dime más", "mas_opciones"),
    ("qué más tienes", "mas_opciones"),
    ("otras opciones", "mas_opciones"),
    ("muéstrame más", "mas_opciones"),
    ("tienes algo diferente", "cambiar_busqueda"),
    ("no me gustó eso", "feedback_negativo"),
    
    # Aclaraciones
    ("qué quieres decir", "explicacion"),
    ("no entendí", "explicacion"),
    ("puedes explicar", "explicacion"),
    ("cómo funciona", "explicacion"),
    ("qué significa eso", "explicacion"),
    
    # Expresiones de interés
    ("interesante", "feedback_positivo"),
    ("me gusta", "feedback_positivo"),
    ("genial", "feedback_positivo"),
    ("wow", "feedback_positivo"),
    ("qué bueno", "feedback_positivo"),
    ("excelente", "feedback_positivo"),
    
    # Expresiones de desinterés
    ("no me interesa", "feedback_negativo"),
    ("no me gustó", "feedback_negativo"),
    ("no me gusta", "feedback_negativo"),
    ("no me gustó eso", "feedback_negativo"),
    ("otra cosa", "cambiar_busqueda"),
    ("aburrido", "feedback_negativo"),
    ("no es lo que busco", "cambiar_busqueda"),
    ("algo diferente", "cambiar_busqueda"),
    
    # Consultas avanzadas (búsquedas con criterios múltiples)
    ("busco libros de terror de no más de 400 páginas", "consulta_avanzada"),
    ("libros de romance menos de 300 págs", "consulta_avanzada"),
    ("ficción de no más de 200 páginas", "consulta_avanzada"),
    ("libros de 2020 en adelante", "consulta_avanzada"),
    ("género suspenso entre 250 y 350 páginas", "consulta_avanzada"),
    ("terror con máximo 500 páginas", "consulta_avanzada"),
    
    # Más conversación casual (para detectar bien)
    ("cómo estás", "Conversacion_Casual"),
    ("como estas", "Conversacion_Casual"),
    ("¿cómo estás?", "Conversacion_Casual"),
    ("qué tal estás", "Conversacion_Casual"),
    ("cómo te va", "Conversacion_Casual"),
    ("cómo andas", "Conversacion_Casual"),
]

def train_model():
    print("Iniciando entrenamiento del modelo.")
    
    # Separar datos
    X = [data[0] for data in training_data]
    y = [data[1] for data in training_data]
    
    # Vectorizar texto
    vectorizer = TfidfVectorizer()
    X_vectors = vectorizer.fit_transform(X)
    
    # Entrenar clasificador
    print("Entrenando clasificador...")
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_vectors, y)
    
    # Guardar modelo
    model_path = os.path.join(os.path.dirname(__file__), "chatbot_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump((vectorizer, clf), f)
    
    print(f"Modelo entrenado y guardado en {model_path}")
    
    # Pruebas rápidas
    test_phrases = [
        "hola cómo estás",
        "libros de romance", 
        "recomiéndame algo",
        "qué géneros tienes",
        "no me gustó eso",
        "cuéntame de ti"
    ]
    
    print("Pruebas del modelo:")
    print("-" * 50)
    for phrase in test_phrases:
        vec = vectorizer.transform([phrase])
        pred = clf.predict(vec)[0]
        confidence = max(clf.predict_proba(vec)[0])
        print(f"'{phrase}' → {pred} (confianza: {confidence:.2%})")
    print("-" * 50)

if __name__ == "__main__":
    train_model()
