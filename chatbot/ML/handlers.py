import random
import re

from .search import (
    buscar_libro_por_titulo, buscar_libro_por_autor,
    buscar_libro_por_genero, buscar_libro_por_area,
    buscar_avanzado, extraer_criterios_avanzados,
    buscar_recomendaciones, buscar_recomendaciones_generales,
)
from .context import (
    contexto_chat, actualizar_contexto_busqueda, obtener_info_libro,
    registrar_en_historial, marcar_intension, obtener_ultima_intension, limpieza_contextual
)
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

def handle_recommendation(user_input, request, exclude_ids):
    resultado_reco = []

    libros_previos = contexto_chat.get("ultimos_libros_encontrados", [])
    if not libros_previos and request and hasattr(request, 'session'):
        libros_previos = request.session.get('libros_vistos', []) or []

    seen_ids = set(exclude_ids or [])
    seen_ids.update({l.get('id') for l in libros_previos if l.get('id')})
    exclude_ids = list(seen_ids) if seen_ids else None

    # Intentar obtener el último género o autor buscado de la sesión
    ultimo_genero = contexto_chat.get('ultimo_genero_exitoso')
    ultimo_autor = contexto_chat.get('ultimo_autor_exitoso')
    if not ultimo_genero and request and hasattr(request, 'session'):
        ultimo_genero = request.session.get('ultimo_genero')
    if not ultimo_autor and request and hasattr(request, 'session'):
        ultimo_autor = request.session.get('ultimo_autor')

    if ultimo_genero:
        #Recomendación basada en el último genero visto
        resultado_reco = buscar_libro_por_genero(ultimo_genero, exclude_ids=exclude_ids)
        frase_intro = f"Como estuvimos viendo libros de {ultimo_genero}, te recomiendo estos otros que te gustarán:"
    elif ultimo_autor:
        # Recomendación basada en el ultimo autor visto
        resultado_reco = buscar_libro_por_autor(ultimo_autor, exclude_ids=exclude_ids)
        frase_intro = f"Como vimos libros de {ultimo_autor}, te recomiendo más obras de este autor o similares:"
    else:
        # Recomendación aleatoria si no hay contexto
        resultado_reco = buscar_recomendaciones_generales(exclude_ids=exclude_ids)
        frase_intro = "¡Claro! He seleccionado estos libros variados que son imprescindibles:"

    if resultado_reco and libros_previos:
        ids_previos = {l.get('id') for l in libros_previos if l.get('id')}
        resultado_reco = [l for l in resultado_reco if l.get('id') not in ids_previos]
        if not resultado_reco:
            resultado_reco = buscar_recomendaciones(exclude_ids=exclude_ids)

    if resultado_reco:
        contexto_chat["ultimos_libros_mostrados"] = [l.get("id") for l in resultado_reco if l.get("id")]
        contexto_chat["ultimos_libros_encontrados"] = resultado_reco
        contexto_chat["offset_mas_opciones"] = min(5, len(resultado_reco))

        if request and hasattr(request, 'session'):
            request.session['libros_vistos'] = resultado_reco

        respuesta_libros = construir_respuesta(resultado_reco[:5])
        return f"{frase_intro}\n\n{respuesta_libros}"

    return "No pude encontrar recomendaciones en este momento. ¿Quieres que te sugiera un género específico?"


def handle_search(intent, user_input, request, exclude_ids):
    """Maneja la lógica de búsquedas."""
    resultados = []
    filtros = None
    criterios = extraer_criterios_avanzados(user_input)
    genero_detectado = None
    if isinstance(criterios.get('generos'), list) and criterios.get('generos'):
        genero_detectado = criterios['generos'][0]
    termino = None
    if intent != "consulta_avanzada":
        termino = criterios.get('autor') or criterios.get('area') or genero_detectado or user_input.split()[-1]

    if intent == "consulta_avanzada":
        filtros = criterios
        resultados = buscar_avanzado(criterios, exclude_ids) if criterios else []
        if not resultados:
            return "No encontré libros con esos filtros. ¿Intentamos con menos páginas o solo el género?"
    elif intent == "buscar_titulo":
        # Limpiar filtros anteriores para búsquedas de título específicas.
        contexto_chat['current_genre'] = None
        contexto_chat['ultimo_genero_exitoso'] = None
        contexto_chat['ultimo_autor_exitoso'] = None
        if request and hasattr(request, 'session'):
            request.session['ultimo_genero'] = None
            request.session['ultimo_autor'] = None

        from .utils import es_entrada_valida
        if not es_entrada_valida(termino):
            return "Vaya, no entiendo eso. ¿Podemos intentar buscando un libro por su nombre?"
        resultados = buscar_libro_por_titulo(termino, exclude_ids)
    elif intent == "buscar_autor":
        from .utils import extraer_nombre_autor
        nombre_limpio = extraer_nombre_autor(user_input)
        resultados = buscar_libro_por_autor(nombre_limpio, exclude_ids)

    elif intent == "buscar_genero":
        resultados = buscar_libro_por_genero(termino, exclude_ids)
    elif intent == "buscar_area":
        resultados = buscar_libro_por_area(termino, exclude_ids)

    if resultados:
        if intent in ["consulta_avanzada", "buscar_autor", "buscar_genero", "buscar_area"] and len(resultados) < 5:
            candidate_books = []
            if intent == "consulta_avanzada":
                criterios = extraer_criterios_avanzados(user_input)
                if criterios:
                    criterios_ampliados = criterios.copy()
                    # Mantener filtros de páginas (max_paginas, min_paginas) - nunca quitar restricciones del usuario
                    criterios_ampliados.pop("area", None)  # Ampliar removiendo área, no páginas
                    candidate_books = buscar_avanzado(criterios_ampliados, exclude_ids) or []
            elif intent == "buscar_autor":
                candidate_books = buscar_libro_por_autor(termino, exclude_ids) or []
            elif intent == "buscar_genero":
                candidate_books = buscar_libro_por_genero(termino, exclude_ids) or []
            elif intent == "buscar_area":
                candidate_books = buscar_libro_por_area(termino, exclude_ids) or []

            for libro in candidate_books:
                if libro not in resultados:
                    resultados.append(libro)
                if len(resultados) >= 5:
                    break

        contexto_chat["ultimos_libros_mostrados"] = [l.get("id") for l in resultados if l.get("id")]
        contexto_chat["ultimos_libros_encontrados"] = resultados
        contexto_chat["offset_mas_opciones"] = min(5, len(resultados))

        resultados_para_mostrar = resultados[:5]

        if request and hasattr(request, 'session'):
            request.session['ultimo_libro_id'] = resultados_para_mostrar[0].get('id')
            request.session['ultimo_libro_titulo'] = resultados_para_mostrar[0].get('titulo')
            request.session['libros_vistos'] = resultados_para_mostrar
            # Guardar el último género o autor buscado para recomendaciones contextuales
            if intent == "buscar_genero":
                request.session['ultimo_genero'] = termino
                contexto_chat['ultimo_genero_exitoso'] = termino
            elif intent == "buscar_autor":
                request.session['ultimo_autor'] = termino
                contexto_chat['ultimo_autor_exitoso'] = termino

        texto_libros = construir_respuesta(resultados_para_mostrar, filtros)
        respuesta_base = _handler_responses.get(intent, "Voy a buscar libros para ti.")
        return f"{respuesta_base}\n\n{texto_libros}"

    return None


def handle_info_libro(user_input, request):
    """Maneja la solicitud de información de libro."""
    from .config import supabase
    ultimos_libros = contexto_chat.get("ultimos_libros_encontrados", [])
    libros_previos = []
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
                    
                    # Paso 1: ficha corta + resumen corto
                    contexto_chat['libro_actual'] = libro
                    contexto_chat['esperando_confirmacion_sinop'] = True
                    contexto_chat['esperando_confirmacion_info'] = False

                    respuesta = (
                        f"{libro['titulo']}\n"
                        f"Autor: {libro.get('autor', 'Desconocido')}\n"
                        f"Año: {libro.get('año_publicacion')}\n"
                        f"Género: {libro.get('gen')}\n"
                        f"Páginas: {libro.get('num_paginas')}\n"
                        f"Área: {libro.get('area')}\n\n"
                        f"Resumen: {libro.get('info')}\n\n"
                        f"¿Deseas conocer la sinopsis completa? (sí/no)"
                    )
                    return respuesta
            except Exception:
                pass

    if ultimos_libros:
        primer_libro = ultimos_libros[0]
        contexto_chat["esperando_confirmacion_info"] = False
        return construir_respuesta_info(primer_libro)

    return "No tengo información de libros anteriores. Primero busca un libro y luego pide 'dame info'."


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