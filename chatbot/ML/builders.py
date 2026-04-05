from .utils import formatear_resultados


def construir_info_resumida(libro):
    if not libro:
        return "No tengo información del libro solicitado."
    
    titulo = libro.get('titulo', 'Título desconocido')
    autor = libro.get('autor', 'Autor desconocido')
    anio = libro.get('año_publicacion', libro.get('anio', 'Desconocido'))
    genero = libro.get('gen', libro.get('genero', 'Desconocido'))
    paginas = libro.get('num_paginas', 'Desconocido')
    area = libro.get('area', 'No especificada')
    sinopsis_texto = libro.get('Sinop') or libro.get('info') or "No disponible"
    
    respuesta = f"""
{titulo}
Autor: {autor}
Año: {anio}
Género: {genero}
Páginas: {paginas}
Área: {area}

Resumen: {sinopsis_texto}"""
    
    return respuesta.strip()


def construir_respuesta_info(libro):
    if not libro:
        return "No tengo información del libro solicitado."
    
    titulo = libro.get('titulo', 'Título desconocido')
    autor = libro.get('autor', 'Autor desconocido')
    anio = libro.get('año_publicacion', libro.get('anio', 'Desconocido'))
    genero = libro.get('gen', libro.get('genero', 'Desconocido'))
    paginas = libro.get('num_paginas', 'Desconocido')
    sinopsis_texto = libro.get('Sinop') or libro.get('info') or "No disponible"
    area = libro.get('area', 'No especificada')
    
    respuesta = f"""
{titulo}
Autor: {autor}
Año: {anio}
Género: {genero}
Páginas: {paginas}
Área: {area}

Sinopsis:
{sinopsis_texto}"""
    
    return respuesta.strip()


def construir_respuesta(libros, filtros=None):
    """Construye una respuesta con lista de libros y pregunta si quiere más info."""
    if not libros:
        return "No encontré libros con esos filtros. ¿Intentamos con otro género o extensión?"

    top_5 = libros[:5]
    lista_libros = ""

    for i, libro in enumerate(top_5, 1):
        titulo = libro.get('titulo', 'Título desconocido')
        autor = libro.get('autor', 'Autor desconocido')
        anio = libro.get('año_publicacion', libro.get('anio', 'Desconocido'))
        genero = libro.get('gen', libro.get('genero', 'Desconocido'))
        paginas = libro.get('num_paginas', 'Desconocido')
        lista_libros += f"{i}. {titulo} - {autor} ({anio}) | {genero} | {paginas} págs\n"

    cierre = (
        "\n¿Te gustaría conocer la sinopsis de alguno de estos libros? "
        "Puedes escribir el título del libro o decir 'dame info' para el primero."
    )
    
    from .context import contexto_chat
    contexto_chat["esperando_confirmacion_info"] = False
    
    return lista_libros + cierre