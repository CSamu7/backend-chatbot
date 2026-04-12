from typing import Dict, List
import difflib
import random
import re
from .config import supabase
from .utils import remover_acentos

def obtener_id_libro(libro: Dict):
    for key in ("id_libro", "id", "libro_id", "ID"):
        if libro.get(key) is not None:
            return libro.get(key)
    return None

def buscar_recomendaciones(limit: int = 5, exclude_ids: List[int] = None) -> List[Dict]:
    try:
        if exclude_ids:
            exclude_ids = [int(id) for id in exclude_ids if str(id).isdigit()]
        
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)

        result = query.limit(max(limit * 4, 20)).execute()
        datos = result.data or []
        if not datos: return []

        unique_books = {obtener_id_libro(l): l for l in datos if obtener_id_libro(l) is not None}
        libros = list(unique_books.values())
        return random.sample(libros, min(limit, len(libros)))
    except Exception as e:
        print(f"Error en búsqueda de recomendaciones: {e}")
        return []

def buscar_recomendaciones_generales(limit: int = 5, exclude_ids: List[int] = None) -> List[Dict]:
    try:
        if exclude_ids:
            exclude_ids = [int(id) for id in exclude_ids if str(id).isdigit()]
        
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)

        result = query.limit(20).execute()
        datos = result.data or []
        if datos:
            return random.sample(datos, k=min(limit, len(datos)))
        return []
    except Exception as e:
        print(f"Error en recomendación general: {e}")
        return []

def buscar_libro_por_titulo(titulo: str, exclude_ids: List[int] = None) -> List[Dict]:
    if not titulo or not titulo.strip(): return []
    try:
        titulo_limpio = remover_acentos(titulo.lower().strip())
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)

        result = query.ilike("titulo", f"%{titulo_limpio}%").execute()
        return result.data or []
    except Exception as e:
        print(f"Error en búsqueda por título: {e}")
        return []

def buscar_libro_por_autor(autor: str, exclude_ids: List[int] = None) -> List[Dict]:
    if not autor or not autor.strip(): return []
    try:
        autor_limpio = remover_acentos(autor.lower().strip())
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)

        result = query.ilike("autor", f"%{autor_limpio}%").execute()
        return result.data or []
    except Exception as e:
        print(f"Error en búsqueda por autor: {e}")
        return []

def buscar_libro_por_genero(genero: str, exclude_ids: List[int] = None) -> List[Dict]:
    if not genero: return []
    try:
        genero_busqueda = remover_acentos(genero.lower().strip())
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)
        
        query = query.ilike("gen", f"%{genero_busqueda}%")
        response = query.limit(20).execute()
        return response.data or []
    except Exception as e:
        print(f"Error en búsqueda por género: {e}")
        return []

def buscar_libro_por_area(area: str, exclude_ids: List[int] = None) -> List[Dict]:
    try:
        area_normalizada = remover_acentos(area.lower().strip())
        query = supabase.table("libros").select("*").ilike("area", f"%{area_normalizada}%")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)
        result = query.execute()
        return result.data or []
    except Exception as e:
        print(f"Error en búsqueda por área: {e}")
        return []

def buscar_avanzado(criterios: Dict, exclude_ids: List[int] = None) -> List[Dict]:
    try:
        query = supabase.table("libros").select("*")
        if exclude_ids:
            query = query.not_.in_("id_libro", exclude_ids)

        if criterios.get("autor"):
            query = query.ilike("autor", f"%{criterios['autor']}%")
        if criterios.get("area"):
            query = query.ilike("area", f"%{remover_acentos(criterios['area'].lower())}%")
        
        genero_principal = None
        if criterios.get("generos"):
            genero_principal = criterios["generos"][0] if isinstance(criterios["generos"], list) else criterios["generos"]
            query = query.ilike("gen", f"%{remover_acentos(genero_principal.lower())}%")

        # Ejecutar consulta inicial
        result = query.execute()
        libros = result.data or []

        # Si no encontró libros con género y hay filtro de género, intentar fallback
        if not libros and genero_principal:
            genero_normalizado = remover_acentos(genero_principal.lower())
            query = supabase.table("libros").select("*")
            if exclude_ids:
                query = query.not_.in_("id_libro", exclude_ids)
            if criterios.get("autor"):
                query = query.ilike("autor", f"%{criterios['autor']}%")
            if criterios.get("area"):
                area_normalizada = remover_acentos(criterios['area'].lower().strip())
                query = query.ilike("area", f"%{area_normalizada}%")
            
            result = query.execute()
            if result.data:
                libros_filtrados = []
                for libro in result.data:
                    gen_val = libro.get("gen", "") or ""
                    if genero_normalizado in remover_acentos(gen_val.lower()):
                        libros_filtrados.append(libro)
                libros = libros_filtrados
        
        # Post-procesamiento para campos numéricos (páginas y año)
        if criterios.get("min_paginas") or criterios.get("max_paginas") or criterios.get("min_año") or criterios.get("max_año"):
            min_p = criterios.get("min_paginas")
            max_p = criterios.get("max_paginas")
            min_a = criterios.get("min_año")
            max_a = criterios.get("max_año")
            libros_filtrados = []
            
            for libro in libros:
                try:
                    # Filtro de páginas
                    if min_p or max_p:
                        try:
                            num_pags = int(libro.get("num_paginas", 0))
                            if min_p and num_pags < int(min_p):
                                continue
                            if max_p and num_pags > int(max_p):
                                continue
                        except (ValueError, TypeError):
                            continue
                    
                    # Filtro de año
                    if min_a or max_a:
                        try:
                            year = int(libro.get("año_publicacion", 0))
                            if min_a and year < int(min_a):
                                continue
                            if max_a and year > int(max_a):
                                continue
                        except (ValueError, TypeError):
                            continue
                    
                    libros_filtrados.append(libro)
                except Exception:
                    continue
            
            libros = libros_filtrados
        
        return libros
    except Exception as e:
        print(f"Error en búsqueda avanzada: {e}")
        return []


def extraer_criterios_avanzados(user_input: str) -> Dict:
    import re
    from .utils import remover_acentos
    
    texto = user_input.lower()
    texto_normalizado = remover_acentos(texto)
    criterios = {}

    paginas_patterns = [
        (r'no mas de (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'no m[aá]s de (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'menos de (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'm[aá]ximo (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'de no mas de (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'de no m[aá]s de (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'de m[aá]ximo (\d+)\s*(?:pag|página|páginas|p\.)?', 'max_paginas'),
        (r'al menos (\d+)\s*(?:pag|página|páginas|p\.)?', 'min_paginas'),
        (r'm[ií]nimo (\d+)\s*(?:pag|página|páginas|p\.)?', 'min_paginas'),
    ]

    for pattern, key in paginas_patterns:
        match = re.search(pattern, texto)
        if match:
            criterios[key] = int(match.group(1))

    generos_map = {
        'terror': 'terror',
        'suspenso': 'suspenso',
        'misterio': 'misterio',
        'ciencia ficcion': 'ciencia ficcion',
        'romance': 'romance',
        'drama': 'drama',
        'fantasia': 'fantasia',  
        'aventura': 'aventura',
        'novela': 'novela',
        'realismo magico': 'realismo magico',
        'historico': 'historico',
        'policial': 'policial',
    }

    generos_encontrados = []
    for genero_key, genero_val in generos_map.items():
        if genero_key in texto_normalizado:
            generos_encontrados.append(genero_val)

    if generos_encontrados:
        criterios['generos'] = generos_encontrados

    area_pattern = r'(?:literatura\s+(\w+)|area\s+(.+?)(?:\s|$))'
    area_match = re.search(area_pattern, texto)
    if area_match:
        if area_match.group(1):  # literatura X
            criterios['area'] = f"literatura {area_match.group(1)}"
        elif area_match.group(2):  # area X
            criterios['area'] = area_match.group(2).strip()

    autor_pattern = r'(?:de|del|autor|escritor)\s+((?:[a-záéíóúñ\s\-\.]+?)?)(?:\s+(?:pero|y|de|que|con)|$)'
    autor_match = re.search(autor_pattern, texto)
    if autor_match:
        autor = autor_match.group(1).strip()
        generos_exclusion = ["terror", "ficción", "drama", "romance", "misterio", "fantasia", 
                             "ciencia ficcion", "aventura", "novela", "realismo magico", 
                             "historico", "policial", "suspenso", "suspense", "existencialismo",
                             "modernismo", "sátira", "tragedia", "poesía", "fábula", "infantil",
                             "familiar", "no ficción", "boom", "epopeya", "ficción histórica",
                             "propaganda", "autobiografía", "ensayo", "cuento", "comedia",
                             "distopía", "distopia", "postapocalíptico", "post-apocalíptico",
                             "thriller", "novela negra", "policiaco"]
        
        autor_normalizado = remover_acentos(autor.lower())
        
        if autor and len(autor) > 2 and autor_normalizado not in generos_exclusion:
            criterios['autor'] = autor

    return criterios


def obtener_lista_autores():
    try:
        res = supabase.table("libros").select("autor").execute()
        if res.data:
            # Limpiamos espacios y eliminamos duplicados
            autores = sorted(list(set(libro['autor'] for libro in res.data if libro['autor'])))
            return autores
        return []
    except Exception as e:
        print(f"Error al obtener autores: {e}")
        return []


def obtener_lista_generos():
    try:
        res = supabase.table("libros").select("gen").execute()
        if res.data:
            generos = sorted(list(set(libro.get('gen') for libro in res.data if libro.get('gen'))))
            return generos
        return []
    except Exception as e:
        print(f"Error al obtener géneros: {e}")
        return []