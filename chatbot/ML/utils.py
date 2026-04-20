from typing import Dict, List
import unicodedata
from .context import actualizar_contexto_busqueda


def remover_acentos(texto: str) -> str:
    texto_nfd = unicodedata.normalize('NFD', texto)
    return ''.join(char for char in texto_nfd if unicodedata.category(char) != 'Mn')


def extraer_termino_busqueda(user_input: str, intent: str) -> str:
    texto = user_input.lower()

    frases_completas = [
        "busco libros del autor", "busco libros de", "libros del autor", "libro escrito por",
        "busca el libro llamado", "busca el libro titulado", "busco el libro llamado", "busco el libro titulado",
        "busco el libro", "busca el libro", "tienes el libro", "libro llamado", "libro titulado",
        "buscar libro", "encuentra el libro", "libros de género", "libros de área",
        "qué me recomiendas", "recomiéndame", "alguna recomendación",
        "más información", "dame más info", "cuéntame sobre"
    ]

    for frase in frases_completas:
        texto = texto.replace(frase, "").strip()

    palabras_individuales = [
        "busco", "busca", "buscar", "encuentra", "quiero", "necesito", "dame", "obras", "autor",
        "escritos", "libros", "libro", "género", "tipo", "categoría", "área", "materia",
        "sinopsis", "trama", "resumen", "detalles", "información", "info", "llamado", "titulado"
    ]

    for palabra in palabras_individuales:
        texto = texto.replace(palabra, "").strip()

    import re
    texto = re.sub(r'\s+', ' ', texto).strip()
    texto = re.sub(r'[^\w\s\-\.áéíóúñ]', '', texto).strip()

    return texto


def formatear_resultados(libros: List[Dict]) -> str:
    if not libros:
        return "No se encontraron resultados."

    actualizar_contexto_busqueda(libros)

    resultado = []
    for i, libro in enumerate(libros[:5], 1):
        info = f"{i}. {libro.get('titulo', 'Título desconocido')}"

        if libro.get('autor'):
            info += f" - {libro['autor']}"

        if libro.get('año_publicacion'):
            info += f" ({libro['año_publicacion']})"

        if libro.get('gen'):
            info += f" | {libro['gen']}"

        if libro.get('num_paginas'):
            info += f" | {libro['num_paginas']} págs"

        resultado.append(info)

    if len(libros) > 0:
        resultado.append("\n¿Quieres más información sobre alguno de estos libros? Solo dime el título o 'dame info' para el primero.")

    return "\n".join(resultado)


def formatear_detalles_libro(libro: Dict) -> str:
    if not libro:
        return "No tengo información del libro solicitado."

    titulo = libro.get('titulo', 'Título desconocido')
    autor = libro.get('autor', 'Autor desconocido')
    anio = libro.get('año_publicacion', libro.get('anio', 'Desconocido'))
    genero = libro.get('gen', libro.get('genero', 'Desconocido'))
    paginas = libro.get('num_paginas', 'Desconocido')
    area = libro.get('area', 'No especificada')
    resumen = libro.get('info') or libro.get('Sinop') or 'No disponible'

    mensaje = (
        f"{titulo}\n"
        f"Autor: {autor}\n"
        f"Año: {anio}\n"
        f"Género: {genero}\n"
        f"Páginas: {paginas}\n"
        f"Área: {area}\n\n"
        f"Resumen: {resumen}"
    )

    return mensaje


def es_entrada_valida(texto: str) -> bool:
    """Filtro de seguridad para evitar búsquedas de insultos o palabras sin sentido."""
    # Lista de palabras que NO deben disparar una búsqueda de libro
    prohibidas = ["idiota", "tonto", "estupido", "mierda", "basura", "puto", "imbecil", "estúpido"]
    # Si la palabra es muy corta y no es 'It', o si está en la lista negra
    t = texto.lower().strip()
    if t in prohibidas or (len(t) < 3 and t != "it"):
        return False
    return True


def extraer_nombre_autor(texto: str) -> str:
    t = texto.lower().strip()
    
    # Lista de frases que el usuario suele decir y debemos ignorar
    frases_sobrantes = [
        "busco libros del autor", 
        "busco libros de", 
        "libros de", 
        "del autor", 
        "autor", 
        "busco"
    ]
    
    for frase in frases_sobrantes:
        t = t.replace(frase, "")
    
    return t.strip()  # Nos queda solo "stephen king"

