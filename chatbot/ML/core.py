import random
import re
from typing import Optional
from .config import nlp, ml_model_loaded, vectorizer, clf, supabase
from .search import (
    buscar_libro_por_titulo, buscar_libro_por_autor,
    buscar_libro_por_genero, buscar_libro_por_area,
    buscar_avanzado, extraer_criterios_avanzados,
    buscar_recomendaciones,
)
from .utils import formatear_resultados, extraer_termino_busqueda, remover_acentos
from .context import (
    contexto_chat, actualizar_contexto_busqueda, obtener_info_libro,
    registrar_en_historial, marcar_intension, obtener_ultima_intension, limpieza_contextual
)
from .handlers import (
    handle_confirmacion_cortesia, handle_recommendation, handle_saludo_social, handle_search, handle_info_libro,
    handle_mas_opciones, handle_feedback
)
from .builders import construir_info_resumida, construir_respuesta_info, construir_respuesta



# --- LISTAS PARA PAGINACIÓN ---
GENEROS_DISPONIBLES = [
    "Romance", "Misterio", "Ciencia Ficción", "Fantasía", "Terror", "Histórica", "Drama", "Policial", "Aventura", "Biografía",
    "Autoayuda", "Infantil", "Juvenil", "Poesía", "Filosofía", "Psicología", "Historia", "Ciencias", "Matemáticas", "Medicina",
    "Derecho", "Economía", "Política", "Religión", "Arte", "Música", "Cine", "Teatro", "Deportes", "Viajes"
]

AUTORES_POPULARES = [
    "Gabriel García Márquez", "Mario Vargas Llosa", "Isabel Allende", "Stephen King", "Julio Cortázar", "Jorge Luis Borges", "Pablo Neruda", "Octavio Paz",
    "Carlos Fuentes", "Juan Rulfo", "Ernest Hemingway", "William Faulkner", "F. Scott Fitzgerald", "John Steinbeck", "Mark Twain", "Edgar Allan Poe",
    "H.P. Lovecraft", "Bram Stoker", "Mary Shelley", "Jane Austen", "Charlotte Brontë", "Emily Brontë", "George Orwell", "Aldous Huxley",
    "Ray Bradbury", "Isaac Asimov", "Arthur C. Clarke", "Philip K. Dick", "Frank Herbert", "J.R.R. Tolkien"
]

# --- CONFIGURACIÓN DE RESPUESTAS ---
intents = {
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
    "mas_opciones": ["dime mas", "que mas tienes", "otras opciones", "muestrame mas", "dame otros 10"],
    "cambiar_busqueda": ["tienes algo diferente", "no me gusto eso", "otra cosa", "no es lo que busco", "algo diferente"],
    "feedback_negativo": ["no me interesa", "aburrido"],
    "explicacion": ["que quieres decir", "no entendi", "puedes explicar", "como funciona", "que significa eso"],
    "feedback_positivo": ["interesante", "me gusta", "genial", "wow", "que bueno", "excelente"]
}

responses = {
    "saludo": [
        "¡Hola! Soy Bookbot, tu asistente de recomendaciones de libros. ¿En qué puedo ayudarte hoy?",
        "¡Hola! ¿Buscas algún libro en particular o quieres que te recomiende algo?",
        "¡Hola! Tengo una gran colección de libros. ¿Qué tipo de lectura te interesa?"
    ],
    "buscar_titulo": [
        "Voy a buscar ese libro para ti.",
        "Déjame buscar ese título en mi colección.",
        "Buscando el libro que mencionas..."
    ],
    "buscar_autor": [
        "Voy a buscar libros de ese autor.",
        "Déjame encontrar obras de ese escritor.",
        "Buscando libros del autor que mencionas..."
    ],
    "buscar_genero": [
        "Voy a buscar libros de ese género.",
        "Déjame encontrar libros de ese tipo.",
        "Buscando libros del género que mencionas..."
    ],
    "buscar_area": [
        "Voy a buscar libros de esa área.",
        "Déjame encontrar libros de esa temática.",
        "Buscando libros del área que mencionas..."
    ],
    "consulta_avanzada": [
        "Voy a buscar libros con esos criterios específicos.",
        "Aplicando los filtros de búsqueda avanzada...",
        "Buscando libros que cumplan con tus especificaciones..."
    ],
    "recomendacion": [
        "¡Claro! Déjame recomendarte algunos libros excelentes.",
        "Tengo varias recomendaciones para ti. ¿Qué género te interesa?",
        "¡Perfecto! Tengo algunas recomendaciones muy buenas."
    ],
    "despedida": [
        "¡Hasta luego! Espero que encuentres el libro perfecto.",
        "¡Adiós! Vuelve cuando quieras más recomendaciones.",
        "¡Hasta pronto! Que tengas un buen día."
    ],
    "como_estás": [
        "¡Estoy excelente, Gracias por preguntar. ¿Y tú, qué tal estás?",
        "¡Muy bien! Con muchas ganas de recomendarte libros hoy. ¿Cómo va tu día?",
        "Todo de maravilla por aquí, listo para ayudarte. ¿Tú cómo te encuentras?",
        "¡Genial! Mi base de datos está llena de libros increíbles. ¿Y tú cómo estás?",
        "¡Excelente! Preparado para ayudarte a encontrar tu próximo libro favorito. ¿Cómo te sientes hoy?",
        "¡De maravilla! Tengo recomendaciones para todos los gustos. ¿Tú cómo te encuentras?"
    ],
    "estado_bot": [
        "Soy Bookbot. Mi trabajo es ayudarte a encontrar el libro perfecto en nuestra base de datos.",
        "Estoy aquí para asistirte en la búsqueda de libros por título, autor o género."
    ],
    "presentacion": [
        "Soy Bookbot, un asistente especializado en recomendaciones de libros. Puedo ayudarte a encontrar libros por título, autor, género o área de estudio.",
        "Me llamo Bookbot y mi especialidad es recomendar libros. Tengo una gran colección organizada por diferentes criterios."
    ],
    "capacidades": [
        "Puedo ayudarte a buscar libros por título, autor, género o área de estudio. También puedo hacer recomendaciones personalizadas.",
        "Mis capacidades incluyen búsqueda avanzada con filtros, recomendaciones personalizadas y información detallada sobre libros."
    ],
    "estadisticas": [
        "Tengo una colección diversa de libros de diferentes géneros y autores.",
        "Mi colección incluye libros de literatura, ciencia, historia y muchos otros temas."
    ],
    "generos_disponibles": [
        "Estos son géneros disponibles en mi biblioteca:\n\n- Romance\n- Misterio\n- Ciencia Ficción\n- Fantasía\n- Terror\n- Histórica\n- Drama\n- Policial\n- Aventura\n- Biografía\n- Autoayuda\n- Infantil\n- Juvenil\n- Poesía\n- Filosofía\n- Psicología\n- Historia\n- Ciencias\n- Matemáticas\n- Medicina\n- Derecho\n- Economía\n- Política\n- Religión\n- Arte\n- Música\n- Cine\n- Teatro\n- Deportes\n- Viajes\n\n¿Quieres ver otros 10? (di 'dame otros 10')"
    ],
    "autores_populares": [
        "Estos son autores disponibles en mi biblioteca:\n\n- Gabriel García Márquez\n- Mario Vargas Llosa\n- Isabel Allende\n- Stephen King\n- Julio Cortázar\n- Jorge Luis Borges\n- Pablo Neruda\n- Octavio Paz\n- Carlos Fuentes\n- Juan Rulfo\n- Ernest Hemingway\n- William Faulkner\n- F. Scott Fitzgerald\n- John Steinbeck\n- Mark Twain\n- Edgar Allan Poe\n- H.P. Lovecraft\n- Bram Stoker\n- Mary Shelley\n- Jane Austen\n- Charlotte Brontë\n- Emily Brontë\n- George Orwell\n- Aldous Huxley\n- Ray Bradbury\n- Isaac Asimov\n- Arthur C. Clarke\n- Philip K. Dick\n- Frank Herbert\n- J.R.R. Tolkien\n\n¿Quieres ver otros 10? (di 'dame otros 10')"
    ],
    "mas_opciones": [
        "Aquí tienes más opciones de libros que podrían interesarte.",
        "Te muestro algunas alternativas más.",
        "Aquí tienes otras recomendaciones."
    ],
    "cambiar_busqueda": [
        "Entiendo. ¿Qué tipo de libro te gustaría buscar?",
        "No hay problema. ¿Qué otro género o autor te interesa?",
        "Vamos a cambiar de búsqueda. ¿Qué te gustaría leer?"
    ],
    "feedback_negativo": [
        "Lamento que no te haya gustado. ¿Quieres probar con otro género?",
        "Entiendo. ¿Te gustaría que busque algo diferente?"
    ],
    "explicacion": [
        "Puedo ayudarte a buscar libros por diferentes criterios: título, autor, género, área de estudio o con filtros avanzados como número de páginas.",
        "Mis funciones incluyen búsqueda básica y avanzada, recomendaciones personalizadas y respuestas a preguntas sobre mi colección."
    ],
    "feedback_positivo": [
        "¡Me alegra que te haya gustado! ¿Quieres que te recomiende algo similar?",
        "¡Excelente! Tengo más libros del mismo estilo si te interesa.",
        "¡Genial! ¿Te gustaría ver más opciones similares?"
    ],
    "respuesta_como_estas": [
        "¡Me alegra oír eso! ¿En qué puedo ayudarte con libros hoy?",
        "¡Excelente! ¿Buscas alguna recomendación o tienes un libro en mente?",
        "¡Genial! Estoy aquí para ayudarte con cualquier consulta sobre libros.",
        "¡Qué bueno! Tengo una gran colección de libros. ¿Qué te gustaría leer?",
        "¡Fantástico! ¿Quieres que te recomiende algo o buscas un libro específico?",
        "¡Me alegra! ¿En qué puedo asistirte hoy con recomendaciones de libros?"
    ],
    "info_libro": [
        "Aquí tienes la información completa del libro:",
        "Te muestro los detalles del libro:"
    ],
    "default": [
        "No estoy seguro de entender tu consulta. ¿Puedes ser más específico sobre qué tipo de libro buscas?",
        "Disculpa, no entendí bien. ¿Quieres buscar por título, autor, género o área de estudio?",
        "Lo siento, no pude interpretar tu mensaje. ¿Puedes reformularlo?"
    ]
}

quick_intentions = {
    "saludo": {
        "keywords": ["hola", "buenos dias", "buenas tardes", "buenas noches", "que tal", "hey", "saludos"],
        "response": "¡Hola! ¿En qué puedo ayudarte con libros hoy?"
    },
    "rechazo": {
        "keywords": ["no", "nada", "ninguno", "no gracias", "no quiero"],
        "response": "Entiendo. ¿Hay algo más en lo que pueda ayudarte?"
    },
    "continuacion": {
        "keywords": ["claro", "por supuesto", "me interesa", "me gusta", "excelente", "adelante", "ok", "vale"],
        "response": "¡Perfecto! ¿Qué más te gustaría saber?"
    },
    "agradecer": {
        "keywords": ["gracias", "muchas gracias", "graciasw", "gracias!", "gracias.", "gracias?"],
        "response": "¡De nada! Es un gusto ayudar. ¿Buscamos algo más?"
    },
    "halagos": {
        "keywords": ["genial", "excelente", "fantastico", "increible", "maravilloso", "buen trabajo"],
        "response": "¡Gracias! Me alegra poder ayudarte."
    }
}

def normalize_text(text: str) -> str:
    
    if text is None or not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = remover_acentos(text)
    
    text = re.sub(r"\s+", " ", text)
    return text

def predict_intent(user_input, session=None):
    if user_input is None: return "default" 
    texto = normalize_text(user_input)


    if any(kw in texto for kw in ["dame info", "el primero", "info del primero", "la primera"]):
        return "info_primer_libro"

    palabras_busqueda = ["busco", "buscar", "encuentra", "dame libros", "libros de", "quiero leer", "género", "genero", "autor", "titulo", "area", "área"]
    if any(kw in texto for kw in palabras_busqueda):
        contexto_chat['esperando_confirmacion_sinop'] = False
        contexto_chat['esperando_confirmacion_info'] = False
        contexto_chat['esperando_respuesta_como_estas'] = False
        contexto_chat['libro_actual'] = None
        contexto_chat['libro_seleccionado'] = None
        contexto_chat['libro_seleccionado_para_info'] = None
        if session:
            session['esperando_respuesta_como_estas'] = False
            session['esperando_confirmacion_libro'] = False
            session['ultimo_libro_visto'] = None
            session.modified = True


    esperando = contexto_chat.get('esperando_respuesta_como_estas', False) or (session and session.get('esperando_respuesta_como_estas', False))
    if esperando:
        respuestas_positivas = [
            "bien", "muy bien", "excelente", "genial", "fantastico", "maravilloso", "perfecto", "mejor imposible", "super bien", "estupendo", "positivo"
        ]
        respuestas_negativas = [
            "mal", "muy mal", "regular", "mas o menos", "más o menos", "no muy bien", "triste", "deprimido", "cansado", "agotado", "negativo"
        ]
        
        for palabra in respuestas_positivas + respuestas_negativas:
            patron = rf"\b{re.escape(palabra)}\b"
            if re.search(patron, texto) or palabra in texto or texto.strip() == palabra:
                contexto_chat['esperando_respuesta_como_estas'] = False
                if session:
                    session['esperando_respuesta_como_estas'] = False
                    session.modified = True
                return "respuesta_como_estas"
      
        if len(texto.split()) <= 3 and ("mal" in texto or "bien" in texto):
            contexto_chat['esperando_respuesta_como_estas'] = False
            if session:
                session['esperando_respuesta_como_estas'] = False
                session.modified = True
            return "respuesta_como_estas"
       
        return "default"
    
    confirmaciones = ["si", "claro", "por supuesto", "vale", "acepto", "sinopsis", "me interesa"]
    if any(word in texto for word in confirmaciones):
        return "afirmacion"
    
   
    for key, data in quick_intentions.items():
        if any(re.search(rf"\b{re.escape(remover_acentos(kw))}\b", texto) for kw in data["keywords"]):
            return key

    ultima_respuesta = contexto_chat.get('ultima_respuesta_bot', '').lower()
    if "te ha convencido este libro" in ultima_respuesta:
        if any(kw in texto for kw in ["si", "me interesa", "me gusta", "comprar", "claro", "por supuesto"]):
            return "libro_accepted"
        if any(kw in texto for kw in ["no", "no gracias", "luego", "despues", "otro"]):
            return "fin_info"

    negaciones = ["no", "gracias", "nelson", "ahora no"]
    if any(word in texto for word in negaciones):
        contexto_chat['esperando_confirmacion_sinop'] = False
        return "fin_info"

    if any(remover_acentos(kw) in remover_acentos(texto) for kw in ["que generos tienes", "que generos hay", "generos disponibles", "que generos ofreces", "que tipos de libros", "cuales son los generos", "que generos manejas", "generos que tienes"]):
        return "generos_disponibles"

    if any(remover_acentos(kw) in remover_acentos(texto) for kw in ["autores populares", "que autores tienes", "autores disponibles", "que autores hay", "autores que tienes", "muestrame autores", "dime autores", "cuales son los autores"]):
        return "autores_populares"

    if any(kw in texto for kw in ["busco", "buscar", "libros de", "quiero libros", "tienes libros", "hay libros", "tienes de"]):
        return "consulta_avanzada"

    # Lógica específica para búsquedas directas
    if "busco libros de" in texto or "buscar libros de" in texto:
        partes = texto.split("de", 1)
        if len(partes) > 1:
            termino = partes[1].strip().lower()
            if any(g.lower() == termino for g in GENEROS_DISPONIBLES):
                return "buscar_genero"
            elif any(a.lower() in termino or termino in a.lower() for a in AUTORES_POPULARES):
                return "buscar_autor"
            else:
                return "consulta_avanzada"

    if contexto_chat.get("esperando_confirmacion_info", False):
        if any(kw in texto for kw in ["si", "sí", "claro", "por supuesto", "adelante", "ok", "vale"]):
            return "info_libro"
        if any(kw in texto for kw in ["no", "nada", "ninguno", "no gracias", "no quiero"]):
            contexto_chat['esperando_confirmacion_info'] = False
            return "fin_info"

    if ml_model_loaded:
        try:
            X = vectorizer.transform([user_input])
            probs = clf.predict_proba(X)[0]
            if max(probs) > 0.7:
                return clf.predict(X)[0]
        except:
            pass

    for intent_name, kws in intents.items():
        for kw in kws:
            if remover_acentos(kw) in texto:
                return intent_name

    if any(kw in texto for kw in ["recomienda", "recomendame", "sugiere", "recomiéndame"]):
        return "recomendacion"

    non_title_keywords = ["que", "como", "donde", "cuando", "por que", "quien", "gracias", "adios", "hasta", "nos vemos", "chao", "bye", "recomienda", "sugiere", "recomendame"]
    if 1 <= len(user_input.strip()) <= 100 and not any(kw in texto for kw in non_title_keywords):
        if contexto_chat.get("ultimos_libros_encontrados"):
            for libro in contexto_chat.get("ultimos_libros_encontrados", []):
                titulo_normalizado = normalize_text(libro.get('titulo', ''))
                if titulo_normalizado in texto or texto in titulo_normalizado:
                    contexto_chat["libro_seleccionado"] = libro
                    contexto_chat["esperando_confirmacion_info"] = True
                    return "mostrar_libro_seleccionado"
            return "buscar_titulo"

    return "default"

def get_response(intent: str, user_input: str, request=None, exclude_ids: list = None) -> str:
    global contexto_chat
    if 'contexto_chat' not in globals():
        contexto_chat = {}

    mensaje_norm = normalize_text(user_input)
    ultimos_libros = contexto_chat.get("ultimos_libros_encontrados", [])

    if intent == "saludo" or mensaje_norm in ["hola", "buenos dias", "buenas", "que tal"]:
        return "Hola. ¿En qué puedo ayudarte? Puedo recomendarte libros por género, autor o buscar un título específico."

    if intent == "respuesta_como_estas" or any(w in mensaje_norm for w in ["como estas", "cómo estás", "como va"]):
        return "¡Muy bien! Con muchas ganas de recomendarte libros hoy. ¿Cómo va tu día?"

    respuestas_positivas = ["bien", "todo bien", "muy bien", "genial", "excelente", "todo correcto"]
    if mensaje_norm in respuestas_positivas and not contexto_chat.get("esperando_confirmacion_sinop"):
        return "¡Me alegra mucho! ¿En qué puedo ayudarte hoy? ¿Buscas algún autor, género o libro en especial?"

    agradecimientos = ["gracias", "muchas gracias", "ty", "thanks"]
    if any(w in mensaje_norm for w in agradecimientos):
        return "¡De nada! Es un placer ayudarte. ¿Hay algo más que te gustaría buscar?"

    if contexto_chat.get("esperando_confirmacion_sinop"):
        if intent == "afirmacion" or mensaje_norm in ["si", "sí", "claro", "vale", "va"]:
            libro = contexto_chat.get("libro_actual")
            if libro:
                contexto_chat['esperando_confirmacion_sinop'] = False
                sinopsis_texto = libro.get('sinop') or libro.get('Sinop') or "Sinopsis no disponible."
                return f"Sinopsis completa de '{libro['titulo']}':\n\n{sinopsis_texto}\n\n¿Deseas buscar otro libro o explorar más?"
        
        if intent == "negacion" or mensaje_norm in ["no", "nones", "paso"]:
            contexto_chat['esperando_confirmacion_sinop'] = False
            return "Entendido. ¿Qué otra consulta deseas realizar?"

    if intent == "recomendacion" or any(w in mensaje_norm for w in ["recomienda", "recomendacion", "recomiendame", "sugiere"]):
        return handle_recommendation(user_input, request, exclude_ids)

    libro_seleccionado = None
    for lb in ultimos_libros:
        if lb.get('titulo') and normalize_text(lb['titulo']) in mensaje_norm:
            libro_seleccionado = lb
            break

    if libro_seleccionado or (intent in ["info_libro", "info_primer_libro"] and ultimos_libros):
        libro_actual = libro_seleccionado or contexto_chat.get("libro_actual") or ultimos_libros[0]
        book_id = libro_actual.get('id_libro') or libro_actual.get('id')
        if book_id:
            try:
                from .config import supabase
                supa_res = supabase.table('libros').select('*').eq('id_libro', book_id).single().execute()
                if supa_res and supa_res.data:
                    libro = supa_res.data
                    contexto_chat.update({'libro_actual': libro, 'esperando_confirmacion_sinop': True})
                    return f"*{libro['titulo']}*\nAutor: {libro.get('autor')}\nResumen: {libro.get('info') or 'No disponible'}\n\n¿Deseas conocer la sinopsis completa? (si/no)"
            except Exception: pass

    peticiones_mas = ["otros 10", "mas", "más", "siguientes", "dame otros"]
    if any(w in mensaje_norm for w in peticiones_mas) or intent == "mas_opciones":
        tipo = contexto_chat.get('paginacion_tipo')
        lista = contexto_chat.get('paginacion_lista', [])
        indice = contexto_chat.get('paginacion_indice', 0)
        if tipo and lista:
            nuevo_indice = indice + 10
            siguientes = lista[nuevo_indice:nuevo_indice + 10]
            if siguientes:
                contexto_chat['paginacion_indice'] = nuevo_indice
                return f"Aquí tienes otros 10 {tipo}:\n\n" + "\n".join([f"- {item}" for item in siguientes]) + "\n\n¿Deseas ver otros 10?"
            contexto_chat['paginacion_tipo'] = None
            return f"Ya te he mostrado todos los {tipo}. ¿Qué te gustaría buscar?"


    if intent == "generos_disponibles" or any(p in mensaje_norm for p in ["que generos", "lista de generos", "generos tienes"]):
        try:
            from .config import supabase
            result = supabase.table("libros").select("gen").execute()
            if result.data:
                generos = sorted(list(set([l.get('gen', '').strip() for l in result.data if l.get('gen', '').strip()])))
                contexto_chat.update({'paginacion_lista': generos, 'paginacion_tipo': 'géneros', 'paginacion_indice': 0})
                return f"Tengo {len(generos)} géneros. Aquí los primeros 10:\n\n" + "\n".join([f"- {g}" for g in generos[:10]]) + "\n\n¿Quieres ver otros 10?"
        except Exception: pass

    if intent == "autores_disponibles" or any(p in mensaje_norm for p in ["que autores", "lista de autores", "autores tienes"]):
        try:
            from .config import supabase
            result = supabase.table("libros").select("autor").execute()
            if result.data:
                autores = sorted(list(set([l.get('autor', '').strip() for l in result.data if l.get('autor', '').strip()])))
                contexto_chat.update({'paginacion_lista': autores, 'paginacion_tipo': 'autores', 'paginacion_indice': 0})
                return f"Tengo {len(autores)} autores. Aquí los primeros 10:\n\n" + "\n".join([f"- {a}" for a in autores[:10]]) + "\n\n¿Quieres ver otros 10?"
        except Exception: pass

    intents_busqueda = ["consulta_avanzada", "buscar_titulo", "buscar_autor", "buscar_genero", "buscar_area"]
    es_patron_busqueda = any(w in mensaje_norm for w in ["busco libros de", "libros de", "buscar libros de", "encuentra libros de"])
    
    if intent in intents_busqueda or es_patron_busqueda:
        search_intent = intent if intent in intents_busqueda else "consulta_avanzada"
        return handle_search(search_intent, user_input, request, exclude_ids)

    return "No estoy seguro de entender tu consulta. ¿Puedes ser más específico? Por ejemplo: 'busco libros de terror' o '¿qué autores tienes?'"