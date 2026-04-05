from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# Datos de entrenamiento - VERSION CORREGIDA
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
    ("otra cosa", "cambiar_busqueda"),
    ("aburrido", "feedback_negativo"),
    ("no es lo que busco", "cambiar_busqueda"),
    ("algo diferente", "cambiar_busqueda")
]

# Separar en X e y
X = [data[0] for data in training_data]
y = [data[1] for data in training_data]



# Entrenar el modelo
vectorizer = TfidfVectorizer()
X_vectors = vectorizer.fit_transform(X)

clf = LogisticRegression()
clf.fit(X_vectors, y)

# Guardar el modelo
with open("chatbot_model.pkl", "wb") as f:
    pickle.dump((vectorizer, clf), f)

print("Modelo entrenado y guardado en chatbot_model.pkl")

# Probar el modelo
test_phrases = [
    "hola cómo estás",
    "libros de romance", 
    "recomiéndame algo",
    "qué géneros tienes",
    "no me gustó eso",
    "cuéntame de ti"
]

