from typing import Dict, List, Optional

contexto_chat = {
    "ultimo_libro_mencionado": None,
    "ultimos_libros_encontrados": [],
    "ultima_intension": None,
    "esperando_respuesta": False,
    "context_state": "IDLE",
    "estado": "NORMAL",
    "lista_pendiente": [],
    "tipo_lista": "",
    "current_genre": None,
    "historial_conversacion": [] 
}


def actualizar_contexto_busqueda(libros_encontrados: List[Dict]):
    contexto_chat["ultimos_libros_encontrados"] = libros_encontrados
    if libros_encontrados:
        contexto_chat["ultimo_libro_mencionado"] = libros_encontrados[0].get("titulo")


def registrar_en_historial(role: str, contenido: str):
    """Registra el mensaje en el historial de conversación"""
    contexto_chat["historial_conversacion"].append({
        "role": role,
        "contenido": contenido
    })
    # Mantener solo últimos 10 mensajes para evitar memoria infinita
    if len(contexto_chat["historial_conversacion"]) > 10:
        contexto_chat["historial_conversacion"] = contexto_chat["historial_conversacion"][-10:]


def marcar_intension(intension: str, requiere_respuesta: bool = False):
    """Marca la intención actual y si espera respuesta"""
    contexto_chat["ultima_intension"] = intension
    contexto_chat["esperando_respuesta"] = requiere_respuesta



def obtener_ultima_intension() -> Optional[str]:
    """Obtiene la última intención del bot"""
    return contexto_chat.get("ultima_intension")


def limpieza_contextual():
    """Limpia el contexto cuando termina un flujo de conversación"""
    contexto_chat["esperando_respuesta"] = False
    contexto_chat["ultima_intension"] = None


def obtener_info_libro(titulo: str = None) -> str:
    if not titulo or not titulo.strip():
        titulo = contexto_chat.get("ultimo_libro_mencionado")
        if not titulo:
            return "No has mencionado ningún libro específico. ¿Sobre qué libro quieres información?"

    if not titulo:
        return "No pude identificar el libro. Por favor, especifica el título."

    try:
        titulo_limpio = titulo.strip().lower()

        from .search import buscar_libro_por_titulo
        result = buscar_libro_por_titulo(titulo_limpio)
        if result:
            libro = result[0]
            info = libro.get('info', '')
            if info and info.strip():
                from .utils import formatear_detalles_libro
                return formatear_detalles_libro(libro)

        # Fall back to other searches
        for func in [
            lambda: buscar_libro_por_titulo(f"%{titulo_limpio}%"),
            lambda: buscar_libro_por_titulo(titulo_limpio),
        ]:
            libros = func()
            if libros:
                libro = libros[0]
                info = libro.get('info', '')
                if info and info.strip():
                    from .utils import formatear_detalles_libro
                    return formatear_detalles_libro(libro)

        return f"Lo siento, no encontré información detallada sobre '{titulo}'. Verifica que el título esté escrito correctamente."

    except Exception as e:
        print(f"Error obteniendo info del libro: {e}")
        return "Hubo un error al consultar la información del libro."
