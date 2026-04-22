import random
import re
from .search import (
    buscar_libro_por_titulo, buscar_libro_por_autor,
    buscar_libro_por_genero, buscar_libro_por_area,
    buscar_avanzado, extraer_criterios_avanzados,
    buscar_recomendaciones, buscar_recomendaciones_generales,
    obtener_id_libro,
)
from .context import (
    contexto_chat, actualizar_contexto_busqueda, obtener_info_libro,
    registrar_en_historial, marcar_intension, obtener_ultima_intension, limpieza_contextual
)
from chat.models import Message
from .builders import construir_respuesta, formatear_resultados, construir_respuesta_info
from .utils import extraer_termino_busqueda, remover_acentos

_handler_responses = {
    "consulta_avanzada": "Voy a buscar libros con esos criterios específicos.",
    "buscar_titulo": "Voy a buscar ese libro para ti.",
    "buscar_autor": "Voy a buscar libros de ese autor.",
    "buscar_genero": "Voy a buscar libros de ese género.",
    "buscar_area": "Voy a buscar libros de esa área.",
    "mas_opciones": "Aquí tienes más opciones de libros que podrían interesarte.",
}

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return remover_acentos(text)

def handle_saludo_social(user_input):
    texto = normalize_text(user_input)
    if any(f == texto for f in ["bien", "muy bien", "todo bien", "excelente"]):
        return "Me alegra escucharlo. ¿Deseas buscar algún libro por título, autor o género ahora?"
    if any(f in texto for f in ["como estas", "que tal", "como va"]):
        respuestas = [
            "Muy bien. Con los circuitos llenos de energía para recomendarte algo bueno. ¿Tú cómo te encuentras?",
            "Excelente. Justo estaba terminando de organizar unos estantes virtuales. ¿Cómo va todo por allá?"
        ]
        return random.choice(respuestas)
    return "Hola. Qué gusto verte de nuevo. ¿Qué tipo de libros te apetece explorar hoy?"

def handle_recommendation(user_input, request, exclude_ids):
    vistos_actualizados = list(exclude_ids) if exclude_ids else []
    if request and hasattr(request, 'session'):
        vistos_sesion = request.session.get('libros_vistos_ids', []) 
        for vid in vistos_sesion:
            if vid not in vistos_actualizados:
                vistos_actualizados.append(vid)

    intereses = []
    if request and hasattr(request, 'session'):
        intereses = request.session.get('historial_generos', [])
    if not intereses:
        intereses = contexto_chat.get('historial_generos_backup', [])

    resultado_reco = []
    genero_usado = ""
    frase_intro = ""

    if intereses:
        for genero in reversed(intereses):
            posibles = buscar_libro_por_genero(genero, exclude_ids=vistos_actualizados)
            if posibles:
                resultado_reco = posibles
                genero_usado = genero
                frase_intro = f"Siguiendo con tu interés en **{genero_usado}**, te sugiero estos:"
                break

    if not resultado_reco:
        resultado_reco = buscar_recomendaciones_generales(exclude_ids=vistos_actualizados)
        frase_intro = "He seleccionado estos libros variados que son imprescindibles:"

    if resultado_reco:
        random.shuffle(resultado_reco)
        final = resultado_reco[:5]

        if request and hasattr(request, 'session'):
            ids_finales = [obtener_id_libro(l) for l in final]
            vistos_actualizados = list(set(vistos_actualizados) | set(ids_finales))
            request.session['libros_vistos_ids'] = vistos_actualizados

        contexto_chat["ultimos_libros_encontrados"] = resultado_reco 
        contexto_chat["offset_mas_opciones"] = 5
        
        return f"{frase_intro}\n\n{construir_respuesta(final)}"

    return "No encontré libros para recomendarte ahora. ¿Buscamos por un género específico?"

def handle_search(intent, user_input, request, exclude_ids):
    user_input = user_input.encode('utf-8', 'replace').decode('utf-8')
    resultados = []
    criterios = extraer_criterios_avanzados(user_input)
    
    intereses = []
    if request and hasattr(request, 'session'):
        intereses = request.session.get('historial_generos', [])
    if not intereses:
        intereses = contexto_chat.get('historial_generos_backup', [])

    genero_detectado = criterios['generos'][0] if (criterios.get('generos')) else None
    termino = criterios.get('autor') or criterios.get('area') or genero_detectado or user_input.split()[-1]

    if intent == "buscar_titulo":
        resultados = buscar_libro_por_titulo(termino, exclude_ids)
    elif intent == "buscar_genero":
        resultados = buscar_libro_por_genero(termino, exclude_ids)
        if resultados and termino not in intereses:
            intereses.append(termino)
    elif intent == "consulta_avanzada":
        resultados = buscar_avanzado(criterios, exclude_ids)

    if resultados:
        contexto_chat["ultimos_libros_encontrados"] = resultados
        if request and hasattr(request, 'session'):
            request.session['historial_generos'] = intereses
        contexto_chat['historial_generos_backup'] = intereses
        return f"{_handler_responses.get(intent, 'Aquí tienes:')}\n\n{construir_respuesta(resultados[:5])}"

    return None

def handle_info_libro(user_input, request):
    from .config import supabase
    ultimos_libros = contexto_chat.get("ultimos_libros_encontrados", [])
    mensaje = normalize_text(user_input)
    libro_seleccionado = None

    for lb in ultimos_libros:
        if normalize_text(lb.get('titulo', '')) in mensaje or mensaje in normalize_text(lb.get('titulo', '')):
            libro_seleccionado = lb
            break

    if libro_seleccionado:
        book_id = libro_seleccionado.get('id_libro') or libro_seleccionado.get('id')
        try:
            supa_res = supabase.table('libros').select('*').eq('id_libro', book_id).single().execute()
            if supa_res and supa_res.data:
                libro = supa_res.data
                return f"**{libro['titulo']}**\nGénero: {libro.get('gen')}\n\n{libro.get('info')}\n\n¿Quieres la sinopsis completa?"
        except: pass
    return "No encontré información detallada sobre ese libro."

def handle_confirmacion_cortesia(user_input):
    """
    Maneja respuestas afirmativas del usuario cuando no hay una búsqueda activa,
    manteniendo la fluidez de la conversación.
    """
    respuestas = [
        "¡Excelente! Dime qué libro, autor o género tienes en mente.",
        "Perfecto. Estoy listo para buscar. ¿Qué te gustaría leer?",
        "Genial. ¿Buscas algo de un área específica o prefieres una recomendación general?",
        "¡Entendido! ¿Tienes algún título en particular que quieras consultar?"
    ]
    return random.choice(respuestas)


def handle_mas_opciones():
    ultimos = contexto_chat.get("ultimos_libros_encontrados", [])
    offset = contexto_chat.get("offset_mas_opciones", 1)
    siguientes = ultimos[offset:offset+5]
    if siguientes:
        contexto_chat["offset_mas_opciones"] += len(siguientes)
        contexto_chat["esperando_confirmacion_info"] = False
        return f"{_handler_responses['mas_opciones']}\n\n{formatear_resultados(siguientes)}"
    return "Ya no tengo más libros similares. ¿Quieres buscar otro tema?"

def handle_feedback(intent):
    if intent in ["feedback_negativo", "rechazo"]:
        limpieza_contextual()
        return "Entendido. ¿Qué otro género o autor te gustaría explorar?"
    elif intent in ["agradecer", "halagos"]:
        return "¡De nada! Es un gusto ayudar. ¿Buscamos algo más?"
    return None
def load_chat_history():
    """
    Extrae el historial de mensajes de la base de datos de Django.
    """
    try:
        from chat.models import Message
        # Traemos los últimos 15 mensajes para no saturar
        mensajes = Message.objects.all().order_by('-created_at')[:15]
        # Los devolvemos en orden cronológico inverso (el más nuevo al final)
        return sorted(mensajes, key=lambda x: x.created_at)
    except Exception as e:
        print(f"Error al cargar el historial: {e}")
        return []
