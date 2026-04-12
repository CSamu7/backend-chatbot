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

# Respuestas para manejo de búsquedas
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

def obtener_ids_vistos_del_chat(chat):
    seen_ids = set()
    for libro_ids in Message.objects.filter(chat=chat).values_list('libro_ids', flat=True):
        if libro_ids:
            if isinstance(libro_ids, (list, tuple, set)):
                seen_ids.update(libro_ids)
            else:
                seen_ids.add(libro_ids)
    return list(seen_ids)


def recomendar_libros(chat_actual):
    """Recomienda libros de Fantasía para un chat, excluyendo los ya vistos."""
    ids_vistos = set(obtener_ids_vistos_del_chat(chat_actual))
    if getattr(chat_actual, 'seen_books', None):
        ids_vistos.update(chat_actual.seen_books)

    recomendaciones = buscar_libro_por_genero("Fantasía", exclude_ids=list(ids_vistos))
    if not recomendaciones:
        return "¡Vaya! Ya te recomendé todos los libros de Fantasía que tengo. ¿Quieres probar otro género?"

    random.shuffle(recomendaciones)
    recomendaciones = recomendaciones[:5]

    nuevos_ids = [obtener_id_libro(libro) for libro in recomendaciones if obtener_id_libro(libro) is not None]
    if nuevos_ids:
        if getattr(chat_actual, 'seen_books', None) is None:
            chat_actual.seen_books = []
        chat_actual.seen_books = list(set(chat_actual.seen_books or []) | set(nuevos_ids))
        chat_actual.save(update_fields=['seen_books'])

    return recomendaciones


def handle_recommendation(user_input, request, exclude_ids):
    import sys
    resultado_reco = []
    
    libros_previos = []
    if request and hasattr(request, 'session'):
        libros_previos = request.session.get('libros_vistos', []) or []

    # Revisar los últimos 5 mensajes del usuario para inferir género
    historial = contexto_chat.get("historial_conversacion", [])
    mensajes_usuario = [msg for msg in historial if msg.get("role") == "usuario"][-5:]  # Últimos 5
    genero_de_mensajes = None
    for msg in reversed(mensajes_usuario):  # Del más reciente al más antiguo
        contenido = msg.get("contenido", "").lower()
        if "fantasía" in contenido or "fantasia" in contenido:
            genero_de_mensajes = "Fantasía"
            break

    # btener el último género o autor buscado de la sesión
    ultimo_genero = contexto_chat.get('current_genre') or contexto_chat.get('ultimo_genero_exitoso') or genero_de_mensajes
    ultimo_autor = contexto_chat.get('ultimo_autor_exitoso')
    if not ultimo_genero and request and hasattr(request, 'session'):
        ultimo_genero = request.session.get('ultimo_genero')
    if not ultimo_autor and request and hasattr(request, 'session'):
        ultimo_autor = request.session.get('ultimo_autor')

    if ultimo_genero:
        # Recomendación basada en el último genero visto
        resultado_reco = buscar_libro_por_genero(ultimo_genero, exclude_ids=exclude_ids)
        if resultado_reco:
            frase_intro = f"Como estuvimos viendo libros de {ultimo_genero}, te recomiendo estos otros que te gustarán:"
        else:
            resultado_reco = buscar_recomendaciones_generales(exclude_ids=exclude_ids)
            frase_intro = f"No encontré más libros exactos de {ultimo_genero}, pero aquí tienes otras recomendaciones interesantes:"
    elif ultimo_autor:
        # Recomendación basada en el ultimo autor visto
        resultado_reco = buscar_libro_por_autor(ultimo_autor, exclude_ids=exclude_ids)
        if resultado_reco:
            frase_intro = f"Como vimos libros de {ultimo_autor}, te recomiendo más obras de este autor o similares:"
        else:
            resultado_reco = buscar_recomendaciones_generales(exclude_ids=exclude_ids)
            frase_intro = f"No encontré más libros de {ultimo_autor}, pero te recomiendo estas otras opciones:"
    else:
        # Recomendación aleatoria si no hay contexto
        resultado_reco = buscar_recomendaciones_generales(exclude_ids=exclude_ids)
        frase_intro = "¡Claro! He seleccionado estos libros variados que son imprescindibles:"

    if resultado_reco and libros_previos:
        ids_previos = {obtener_id_libro(l) for l in libros_previos if obtener_id_libro(l) is not None}
        resultado_reco = [l for l in resultado_reco if obtener_id_libro(l) not in ids_previos]
        if not resultado_reco:
            resultado_reco = buscar_recomendaciones(exclude_ids=exclude_ids)

    if resultado_reco:
        contexto_chat["ultimos_libros_mostrados"] = [obtener_id_libro(l) for l in resultado_reco if obtener_id_libro(l) is not None]
        contexto_chat["ultimos_libros_encontrados"] = resultado_reco
        contexto_chat["offset_mas_opciones"] = min(5, len(resultado_reco))

        if request and hasattr(request, 'session'):
            request.session['libros_vistos'] = resultado_reco

        # Actualizar seen_books
        seen_books = set(contexto_chat.get('seen_books', []))
        seen_books.update([obtener_id_libro(l) for l in resultado_reco if obtener_id_libro(l) is not None])
        contexto_chat['seen_books'] = list(seen_books)

        respuesta_libros = construir_respuesta(resultado_reco[:5])
        return f"{frase_intro}\n\n{respuesta_libros}"

    return "No pude encontrar recomendaciones en este momento. ¿Quieres que te sugiera un género específico?"


def handle_search(intent, user_input, request, exclude_ids):
    """Maneja la lógica de búsquedas con persistencia y exclusión inmediata."""
    user_input = user_input.encode('utf-8', 'replace').decode('utf-8')
    
    resultados = []
    filtros = None
    criterios = extraer_criterios_avanzados(user_input)
    
    intereses = []
    if request and hasattr(request, 'session'):
        intereses = request.session.get('historial_generos', [])
    if not intereses:
        intereses = contexto_chat.get('historial_generos_backup', [])

    genero_detectado = criterios['generos'][0] if (criterios.get('generos') and len(criterios['generos']) > 0) else None
    termino = criterios.get('autor') or criterios.get('area') or genero_detectado or user_input.split()[-1]

    if intent == "buscar_titulo":
        resultados = buscar_libro_por_titulo(termino, exclude_ids)
    elif intent == "buscar_genero":
        resultados = buscar_libro_por_genero(termino, exclude_ids)
        if resultados and termino not in intereses:
            intereses.append(termino)
    elif intent == "consulta_avanzada":
        resultados = buscar_avanzado(criterios, exclude_ids)
        if genero_detectado and genero_detectado not in intereses:
            intereses.append(genero_detectado)

    if request and hasattr(request, 'session'):
        request.session['historial_generos'] = intereses
    contexto_chat['historial_generos_backup'] = intereses
    contexto_chat['current_genre'] = intereses[-1] if intereses else None

    if resultados:
       
        if request and hasattr(request, 'session'):
            # Usamos 'libros_vistos_ids' para coincidir con recommendation
            vistos_ids = request.session.get('libros_vistos_ids', []) 
            for lib in resultados[:5]:
                id_actual = lib.get('id_libro') or lib.get('id')
                if id_actual and id_actual not in vistos_ids:
                    vistos_ids.append(id_actual)
            request.session['libros_vistos_ids'] = vistos_ids
        contexto_chat["ultimos_libros_encontrados"] = resultados
        texto_libros = construir_respuesta(resultados[:5], filtros)
        return f"{_handler_responses.get(intent, 'Aquí tienes:')}\n\n{texto_libros}"

    return None

def handle_recommendation(user_input, request, exclude_ids):
    """Cerebro de recomendación con exclusión de duplicados BLINDADA."""

    vistos_actualizados = list(exclude_ids) if exclude_ids else []
    if request and hasattr(request, 'session'):
        # IMPORTANTE: Asegúrate de que esta clave sea la misma que usas en todo tu código
        vistos_sesion = request.session.get('libros_vistos_ids', []) 
        for vid in vistos_sesion:
            if vid not in vistos_actualizados:
                vistos_actualizados.append(vid)

    intereses = []
    if request and hasattr(request, 'session'):
        intereses = request.session.get('historial_generos', [])
    
    if not intereses:
        intereses = contexto_chat.get('historial_generos_backup', [])
    
    if not intereses and contexto_chat.get('libro_actual'):
        gen_ultimo = contexto_chat['libro_actual'].get('gen')
        if gen_ultimo: intereses = [gen_ultimo]

    resultado_reco = []
    genero_usado = ""

    # 2. BÚSQUEDA EN CASCADA (Usando el escudo anti-repetidos)
    for genero in reversed(intereses):
        # ¡AQUÍ ESTÁ LA MAGIA! Pasamos vistos_actualizados, NO exclude_ids
        posibles = buscar_libro_por_genero(genero, exclude_ids=vistos_actualizados)
        if posibles:
            resultado_reco = posibles
            genero_usado = genero
            break

    if not resultado_reco and intereses:
        genero_usado = intereses[-1]
        resultado_reco = buscar_libro_por_genero(genero_usado, exclude_ids=[])
        frase_intro = f"Ya vimos los más recientes de **{genero_usado}**, pero aquí tienes otros destacados:"
    elif resultado_reco:
        frase_intro = f"Siguiendo con tu interés en **{genero_usado}**, te sugiero estos:"
    else:
        resultado_reco = buscar_recomendaciones_generales(exclude_ids=vistos_actualizados)
        frase_intro = "No tengo claro tu género favorito todavía, pero estos libros son excelentes:"

    if resultado_reco:
        import random
        random.shuffle(resultado_reco)
        final = resultado_reco[:5]

        # 3. ACTUALIZAR SESIÓN DE INMEDIATO PARA LA PRÓXIMA
        if request and hasattr(request, 'session'):
            for lib in final:
                id_actual = lib.get('id_libro') or lib.get('id')
                if id_actual and id_actual not in vistos_actualizados:
                    vistos_actualizados.append(id_actual)
            request.session['libros_vistos_ids'] = vistos_actualizados

        contexto_chat["ultimos_libros_mostrados"] = [obtener_id_libro(l) for l in final]
        contexto_chat["ultimos_libros_encontrados"] = resultado_reco 
        
        return f"{frase_intro}\n\n{construir_respuesta(final)}"

    return "No encontré más libros por ahora."

def handle_info_libro(user_input, request):
    """Maneja la info y REFUERZA el género para que la recomendación no falle."""
    from .config import supabase
    ultimos_libros = contexto_chat.get("ultimos_libros_encontrados", [])
    mensaje = normalize_text(user_input)
    libro_seleccionado = None

    # Intentar identificar el libro
    if mensaje in ["si", "sí", "dame info", "info"]:
        libro_seleccionado = contexto_chat.get("libro_seleccionado") or (ultimos_libros[0] if ultimos_libros else None)
    else:
        for lb in ultimos_libros:
            if normalize_text(lb.get('titulo', '')) in mensaje:
                libro_seleccionado = lb
                break

    if libro_seleccionado:
        book_id = libro_seleccionado.get('id_libro') or libro_seleccionado.get('id')
        try:
            supa_res = supabase.table('libros').select('*').eq('id_libro', book_id).single().execute()
            if supa_res and supa_res.data:
                libro = supa_res.data
                gen = libro.get('gen')
                
                
                if gen:
                    contexto_chat['current_genre'] = gen
                    intereses = contexto_chat.get('historial_generos_backup', [])
                    if gen not in intereses: intereses.append(gen)
                    contexto_chat['historial_generos_backup'] = intereses
                    if request and hasattr(request, 'session'):
                        request.session['historial_generos'] = intereses

                contexto_chat['libro_actual'] = libro
                return f"{libro['titulo']}\nGénero: {gen}\n\n{libro.get('info')}\n\n¿Quieres la sinopsis completa?"
        except Exception: pass
    return "No encontré información."


def handle_mas_opciones():
    """Maneja la solicitud de más opciones."""
    ultimos = contexto_chat.get("ultimos_libros_encontrados", [])
    offset = contexto_chat.get("offset_mas_opciones", 1)
    siguientes = ultimos[offset:offset+5]
    if siguientes:
        contexto_chat["offset_mas_opciones"] += len(siguientes)
        contexto_chat["esperando_confirmacion_info"] = False
        return f"{_handler_responses['mas_opciones']}\n\n{formatear_resultados(siguientes)}"
    return "Ya no tengo más libros similares. ¿Quieres buscar otro tema?"


def handle_feedback(intent):
    """Maneja feedback y limpieza."""
    if intent in ["feedback_negativo", "rechazo"]:
        limpieza_contextual()
        return "Entendido. ¿Qué otro género o autor te gustaría explorar?"
    elif intent in ["agradecer", "halagos"]:
        return "¡De nada! Es un gusto ayudar. ¿Buscamos algo más?"
    return None