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
    handle_recommendation, handle_search, handle_info_libro,
    handle_mas_opciones, handle_feedback
)
from .builders import construir_info_resumida, construir_respuesta_info, construir_respuesta

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
    "mas_opciones": ["dime mas", "que mas tienes", "otras opciones", "muestrame mas"],
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
        "¡Estoy excelente, José! Gracias por preguntar. ¿Y tú, qué tal estás?",
        "¡Muy bien! Con muchas ganas de recomendarte libros hoy. ¿Cómo va tu día?",
        "Todo de maravilla por aquí, listo para ayudarte. ¿Tú cómo te encuentras?"
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
        "Tengo libros de romance, misterio, ciencia ficción, fantasía, terror, histórica, drama, policial y muchos más.",
        "Los géneros disponibles incluyen: romance, misterio, ciencia ficción, fantasía, terror, histórica, drama, policial, entre otros."
    ],
    "autores_populares": [
        "Tengo libros de autores como Gabriel García Márquez, Mario Vargas Llosa, Isabel Allende, Stephen King, Julio Cortázar y muchos más.",
        "Mi colección incluye obras de autores clásicos y contemporáneos de habla hispana y universal."
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
        "keywords": ["si", "claro", "por supuesto", "me interesa", "me gusta", "excelente", "adelante", "ok", "vale"],
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
    text = text.lower().strip()
    text = remover_acentos(text)
    text = re.sub(r'[^\w\s]', '', text)
    return text

# --- DETECCIÓN DE INTENCIONES ---

def predict_intent(user_input: str) -> str:
    texto = normalize_text(user_input)

    if any(kw in texto for kw in ["busco", "buscar", "libros de", "género", "genero", "autor", "titulo", "area", "área"]):
        if contexto_chat.get('esperando_confirmacion_sinop', False) or contexto_chat.get('esperando_confirmacion_info', False):
            contexto_chat['esperando_confirmacion_sinop'] = False
            contexto_chat['esperando_confirmacion_info'] = False
            contexto_chat['libro_actual'] = None
            contexto_chat['libro_seleccionado'] = None
            contexto_chat['libro_seleccionado_para_info'] = None

    ultima_respuesta = contexto_chat.get('ultima_respuesta_bot', '').lower()
    if "te ha convencido este libro" in ultima_respuesta:
        if any(kw in texto for kw in ["si", "me interesa", "me gusta", "comprar", "claro", "por supuesto"]):
            return "libro_accepted"
        if any(kw in texto for kw in ["no", "no gracias", "luego", "despues", "otro"]):
            return "fin_info"

    if contexto_chat.get('esperando_confirmacion_sinop', False):
        if any(word in texto for word in ["si", "sí", "claro", "por favor", "adelante", "sip", "me interesa", "me gusta", "excelente"]):
            return "confirmar_sinopsis_larga"
        if any(word in texto for word in ["no", "gracias", "nelson", "luego", "despues"]):
            contexto_chat['esperando_confirmacion_sinop'] = False
            return "fin_info"

    if any(kw in texto for kw in ["busco", "buscar", "libros de", "quiero libros", "tienes libros", "hay libros", "tienes de"]):
        return "consulta_avanzada"

    if any(kw in texto for kw in ["dame info", "mas info", "detalles", "sinopsis"]):
        return "info_libro"

    if any(kw in texto for kw in ["como estas", "como esta", "que tal", "como va"]):
        return "como_estás"

    if any(kw in texto for kw in ["que haces", "que hace", "a que te dedicas"]):
        return "estado_bot"

    if any(kw in texto for kw in ["hablame de ti", "quien eres", "presentate"]):
        return "presentacion"

    if any(kw in texto for kw in ["tienes libros", "hay libros", "tienes de", "busco libros", "quiero libros"]) or any(kw in texto for kw in ["paginas", "menos de", "mas de", "maximo", "minimo", "al menos", "no mas de"]):
        return "consulta_avanzada"

    if any(kw in texto for kw in ["que generos tienes", "que generos hay", "generos disponibles", "que generos ofreces", "que tipos de libros", "cuales son los generos", "que generos manejas", "generos que tienes"]):
        return "generos_disponibles"

    if contexto_chat.get("esperando_confirmacion_info", False):
        if any(kw in texto for kw in ["si", "sí", "claro", "por supuesto", "adelante", "ok", "vale"]):
            return "info_libro"
        if any(kw in texto for kw in ["no", "nada", "ninguno", "no gracias", "no quiero"]):
            contexto_chat['esperando_confirmacion_info'] = False
            return "fin_info"

    for key, data in quick_intentions.items():
        if any(re.search(rf"\b{re.escape(remover_acentos(kw))}\b", texto) for kw in data["keywords"]):
            return key

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

# --- GENERACIÓN DE RESPUESTAS ---

def get_response(intent: str, user_input: str, request=None, exclude_ids: list = None) -> str:
    if exclude_ids is None:
        exclude_ids = contexto_chat.get('seen_books', []) or []
    
    try:
        marcar_intension(intent)
    except Exception:
        pass
    
    feedback_post = contexto_chat.get("estado") == "ESPERANDO_FEEDBACK_POST_SINOP" or contexto_chat.get("context_state") == "ESPERANDO_FEEDBACK_POST_SINOP"
    if intent == "afirmacion" and feedback_post:
        contexto_chat["estado"] = "NORMAL"
        contexto_chat["context_state"] = "IDLE"
        contexto_chat["esperando_confirmacion_sinop"] = False
        contexto_chat["esperando_confirmacion_info"] = False
        result = "¡Me alegra mucho que te haya servido! Disfruta mucho de la lectura. Estaré aquí si necesitas otra recomendación."
        contexto_chat['ultima_respuesta_bot'] = result
        return result

    if intent == "afirmacion":
        if contexto_chat.get("esperando_confirmacion_sinop"):
            libro = contexto_chat.get("libro_actual")
            if libro:
                contexto_chat['esperando_confirmacion_sinop'] = False
                result = (
                    f"Sinopsis completa de '{libro['titulo']}'\n\n"
                    f"{libro.get('Sinop')}\n\n"
                    f"¿Deseas buscar otro libro o explorar más?"
                )
                contexto_chat['ultima_respuesta_bot'] = result
                return result
        return "Entendido!"
    
    if intent == "negacion":
        if contexto_chat.get("esperando_confirmacion_sinop"):
            contexto_chat['esperando_confirmacion_sinop'] = False
            result = "Perfecto. ¿Hay algo más que buscas? Puedo buscar por título, autor, género o área."
            contexto_chat['ultima_respuesta_bot'] = result
            return result
        return "Entendido!"
    
    if intent == "recomendacion":
        return handle_recommendation(user_input, request, exclude_ids)
    
    if intent in ["consulta_avanzada", "buscar_titulo", "buscar_autor", "buscar_genero", "buscar_area"]:
        contexto_chat["esperando_confirmacion_sinop"] = False
        contexto_chat["esperando_confirmacion_info"] = False
        result = handle_search(intent, user_input, request, exclude_ids)
        if result:
            contexto_chat['ultima_respuesta_bot'] = result
            return result
    
    if intent == "mas_opciones":
        result = handle_mas_opciones()
        contexto_chat['ultima_respuesta_bot'] = result
        return result
    
    if intent == "confirmar_sinopsis_larga":
        libro = contexto_chat.get('libro_actual')
        if libro:
            contexto_chat['esperando_confirmacion_sinop'] = False
            contexto_chat['libro_actual'] = None
            result = (
                f"Sinopsis completa de '{libro['titulo']}'\n\n"
                f"{libro.get('Sinop')}\n\n"
                f"¿Te ha convencido este libro o prefieres seguir explorando la lista?"
            )
            contexto_chat['ultima_respuesta_bot'] = result
            return result
        result = "No tengo información del libro seleccionado."
        contexto_chat['ultima_respuesta_bot'] = result
        return result

    # --- CORRECCIÓN AQUÍ PARA 'libros_previos' ---
    if intent == "info_libro":
        ultimos_libros = contexto_chat.get("ultimos_libros_encontrados", [])
        libros_previos = [] # Se inicializa siempre vacía para evitar el Error
        
        if request and hasattr(request, 'session'):
            libros_previos = request.session.get('libros_vistos', []) or []

        mensaje = normalize_text(user_input)
        libro_seleccionado = None

        if mensaje in ["si", "sí", "dame info", "dame información", "info"]:
            libro_seleccionado = contexto_chat.get("libro_seleccionado") or contexto_chat.get("libro_seleccionado_para_info")
            if not libro_seleccionado:
                if libros_previos:
                    libro_seleccionado = libros_previos[0]
                elif ultimos_libros:
                    libro_seleccionado = ultimos_libros[0]
        else:
            libro_seleccionado = contexto_chat.get("libro_seleccionado")
            if not libro_seleccionado:
                for lb in libros_previos:
                    if 'titulo' in lb and normalize_text(lb['titulo']) in mensaje:
                        libro_seleccionado = lb
                        break
            if not libro_seleccionado:
                for lb in ultimos_libros:
                    if normalize_text(lb.get('titulo', '')) in mensaje:
                        libro_seleccionado = lb
                        break

        if libro_seleccionado:
            book_id = libro_seleccionado.get('id_libro') or libro_seleccionado.get('id')
            if book_id is not None:
                try:
                    supa_res = supabase.table('libros').select('*').eq('id_libro', book_id).single().execute()
                    if supa_res and getattr(supa_res, 'data', None):
                        libro = supa_res.data
                        contexto_chat['libro_actual'] = libro
                        contexto_chat['esperando_confirmacion_sinop'] = True
                        contexto_chat['esperando_confirmacion_info'] = False
                        result = construir_info_resumida(libro)
                        result += "\n\nResumen: " + (libro.get('info') or "No disponible")
                        result += "\n\nDeseas conocer la sinopsis completa? (si/no)"
                        contexto_chat['ultima_respuesta_bot'] = result
                        return result
                except Exception:
                    pass

        if ultimos_libros:
            primer_libro = ultimos_libros[0]
            contexto_chat["esperando_confirmacion_info"] = False
            result = construir_respuesta_info(primer_libro)
            contexto_chat['ultima_respuesta_bot'] = result
            return result

        result = "No tengo información de libros anteriores. Primero busca un libro y luego pide 'dame info'."
        contexto_chat['ultima_respuesta_bot'] = result
        return result
    
    if intent == "libro_aceptado":
        result = "¡Excelente elección! Me alegra que te haya gustado. ¿Quieres que busquemos algo más o prefieres otra recomendación?"
        contexto_chat['ultima_respuesta_bot'] = result
        return result
    
    if intent == "mostrar_libro_seleccionado":
        libro = contexto_chat.get("libro_seleccionado")
        if libro:
            contexto_chat["libro_seleccionado_para_info"] = libro
            contexto_chat["libro_actual"] = libro
            contexto_chat["esperando_confirmacion_sinop"] = True
            contexto_chat["esperando_confirmacion_info"] = False
            info = construir_info_resumida(libro)
            result = f"{info}\n\n¿Deseas conocer la sinopsis completa? (sí/no)"
            contexto_chat['ultima_respuesta_bot'] = result
            return result
        result = "No encontré ese libro en los resultados anteriores."
        contexto_chat['ultima_respuesta_bot'] = result
        return result
    
    if intent == "fin_info":
        contexto_chat["esperando_confirmacion_info"] = False
        contexto_chat["esperando_confirmacion_sinop"] = False
        contexto_chat["libro_actual"] = None
        contexto_chat["libro_seleccionado"] = None
        result = "Entendido. ¿Hay algo más en lo que pueda ayudarte? Puedo buscar libros por título, autor, género o área de estudio."
        contexto_chat['ultima_respuesta_bot'] = result
        return result

    if intent == "continuar_busqueda":
        result = "Perfecto, dime qué tipo de libros te gustaría explorar ahora (género, autor, área, etc.)."
        contexto_chat['ultima_respuesta_bot'] = result
        return result

    feedback_result = handle_feedback(intent)
    if feedback_result:
        contexto_chat['ultima_respuesta_bot'] = feedback_result
        return feedback_result
    
    if intent == "generos_disponibles":
        contexto_chat["esperando_confirmacion_sinop"] = False
        contexto_chat["esperando_confirmacion_info"] = False
        try:
            from .config import supabase
            result = supabase.table("libros").select("gen").execute()
            if result.data:
                generos = set()
                for libro in result.data:
                    gen = libro.get('gen', '').strip()
                    if gen:
                        generos.add(gen)
                generos_ordenados = sorted(list(generos))
                generos_texto = ", ".join(generos_ordenados)
                result = f"Estos son todos los géneros disponibles en mi colección:\n\n{generos_texto}\n\n¿Te gustaría buscar libros de algún género específico?"
                contexto_chat['ultima_respuesta_bot'] = result
                return result
        except Exception as e:
            print(f"Error al obtener géneros: {e}")
            pass
    
    res_list = responses.get(intent, responses["default"])
    respuesta_base = random.choice(res_list)
    registrar_en_historial("bot", respuesta_base)
    contexto_chat['ultima_respuesta_bot'] = respuesta_base
    return respuesta_base
