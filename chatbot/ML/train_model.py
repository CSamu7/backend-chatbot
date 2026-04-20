import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Datos de entrenamiento basados en intents
intents_data = {
    "saludo": ["hola", "buenos dias", "buenas tardes", "buenas noches", "que tal", "hey", "saludos"],
    "buscar_titulo": ["busco el libro", "libro llamado", "titulo", "libro titulado"],
    "buscar_area": ["libros de area", "area de", "materia", "campo de estudio", "tematica"],
    "buscar_autor": ["autor", "escritor", "obras de"],
    "buscar_genero": ["libros de genero", "genero", "tipo de libro", "categoria", "novelas de"],
    "recomendacion": ["recomiendame", "que me recomiendas", "alguna recomendacion", "sugiereme"],
    "despedida": ["adios", "hasta luego", "nos vemos", "chao", "bye", "hasta pronto"],
    "como_estás": ["como estás", "como estas", "cómo estás", "cómo estas"],
    "estado_bot": ["que haces", "qué haces"],
    "presentacion": ["hablame de ti", "quien eres"],
    "capacidades": ["de que puedes hablar", "que sabes hacer"],
    "estadisticas": ["cuantos libros tienes"],
    "generos_disponibles": ["que generos disponibles", "que generos tienes", "que tipos de libros", "que categorias", "que generos hay", "muestrame los generos", "dime los generos", "cuales son los generos"],
    "autores_populares": ["autores populares"],
    "mas_opciones": ["dime mas", "que mas tienes", "otras opciones", "muestrame mas"],
    "cambiar_busqueda": ["tienes algo diferente", "no me gusto eso", "otra cosa", "no es lo que busco", "algo diferente"],
    "feedback_negativo": ["no me interesa", "aburrido"],
    "explicacion": ["que quieres decir", "no entendi", "puedes explicar", "como funciona", "que significa eso"],
    "feedback_positivo": ["interesante", "me gusta", "genial", "wow", "que bueno", "excelente"]
}

# Crear dataset
X = []
y = []
for intent, phrases in intents_data.items():
    for phrase in phrases:
        X.append(phrase)
        y.append(intent)

# Vectorizar
vectorizer = TfidfVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Entrenar modelo
clf = SVC(probability=True)
clf.fit(X_vectorized, y)

# Guardar modelo
with open('chatbot_model.pkl', 'wb') as f:
    pickle.dump((vectorizer, clf), f)

print("Modelo entrenado y guardado en chatbot_model.pkl")