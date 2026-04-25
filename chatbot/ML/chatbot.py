import sys

from ML.core import get_response, predict_intent

from .handlers import handle_recommendation
from .utils import remover_acentos
from .context import (
    contexto_chat, registrar_en_historial
)
from .search import buscar_libro_por_titulo, extraer_criterios_avanzados
from .config import Chat, Message, User

def obtener_id_libro(libro):
    """Extrae el ID ya sea de un diccionario o de un objeto de modelo."""
    if isinstance(libro, dict):
        return libro.get('id_libro') or libro.get('id')
    return getattr(libro, 'id_libro', getattr(libro, 'id', None))

def sanitize_text(text: str) -> str:
    if text is None:
        return ""
    safe = text.encode('utf-8', 'replace').decode('utf-8')
    safe = ''.join(ch for ch in safe if not (0xD800 <= ord(ch) <= 0xDFFF))
    return safe.strip()


def infer_genre_from_query(query: str):
    criterios = extraer_criterios_avanzados(query)
    generos = criterios.get('generos')
    if generos:
        return generos[0]
    lower = query.lower()
    if 'libros de ' in lower:
        after = lower.split('libros de ', 1)[1].strip()
        if after:
            return after.split()[0]
    return None


def infer_book_from_bot_prompt(prompt: str):
    prompt_text = (prompt or '').strip()
    if not prompt_text:
        return None

    first_line = prompt_text.splitlines()[0].strip()
    if not first_line:
        return None

    candidates = buscar_libro_por_titulo(first_line)
    if candidates:
        return candidates[0]
    return None


def procesar_comentarios_personales(texto: str):
    t = texto.lower().strip()

    # Categorías de entrada
    insultos = ["tonto", "idiota", "estupido", "malo"]
    halagos = ["genial", "increible", "crack", "maquina", "eres el mejor"]
    agradecimientos = ["gracias", "muchas gracias", "thx", "ty"]

    if any(i in t for i in insultos):
        return "Oye, eso dolió... Pero soy un profesional. ¿Buscamos un libro para mejorar el ánimo?"

    if any(h in t for h in halagos):
        return "¡Oh, me vas a hacer sonrojar! Solo intento ser el mejor bibliotecario posible. ¿Buscamos algo más?"

    if any(a in t for a in agradecimientos):
        return "¡De nada! Es un placer ayudarte a encontrar buenas historias. ¿Te apetece ver algo más o eso sería todo?"

    return None


def respuesta_social(texto: str):
    t = texto.lower().strip()

    if any(kw in t for kw in ["hola", "buenos dias", "buenos días", "buenas", "qué tal", "que tal", "buenas tardes", "buenas noches"]):
        return "¡Hola! Estoy aquí para ayudarte a encontrar libros. ¿Qué te gustaría leer hoy?"

    if any(kw in t for kw in ["qué haces", "que haces", "a que te dedicas"]):
        return "Estoy buscando las mejores recomendaciones para ti. ¿Te interesa algún género en particular?"

    if any(kw in t for kw in ["cómo estás", "como estas", "qué tal", "que tal"]):
        return "Estoy bien, gracias. ¿Qué tipo de libros te apetece explorar hoy?"

    return None


def mostrar_lista_paginada(lista: list, tipo: str) -> str:
    visibles = lista[:10]
    resto = lista[10:]
    contexto_chat['lista_pendiente'] = resto
    contexto_chat['tipo_lista'] = tipo

    lista_formateada = "\n".join([f"* {item}" for item in visibles])

    if resto:
        contexto_chat['estado'] = 'ESPERANDO_PAGINACION'
        return (
            f"Aquí tienes algunos {tipo} destacados:\n\n"
            f"{lista_formateada}\n\n"
            "¿Te interesa alguno de estos o prefieres ver otros 10?"
        )

    contexto_chat['estado'] = 'NORMAL'
    return (
        f"Aquí tienes todos los {tipo} disponibles:\n\n"
        f"{lista_formateada}\n\n"
        "¿Te gustaría buscar a alguno en específico?"
    )


def rehydrate_context_from_loaded_history(chat: Chat, loaded_messages):
    if chat and chat.last_genre:
        contexto_chat['current_genre'] = chat.last_genre

    bot_messages = [text for role, text in loaded_messages if role == 'bot']
    if not bot_messages:
        return

    last_bot_text = bot_messages[-1]
    contexto_chat['ultima_respuesta_bot'] = last_bot_text

    normalized = last_bot_text.lower()
    if '¿deseas conocer la sinopsis completa' in normalized or '¿deseas saber la sinopsis completa' in normalized:
        contexto_chat['esperando_confirmacion_sinop'] = True
        libro = infer_book_from_bot_prompt(last_bot_text)
        if libro:
            contexto_chat['libro_actual'] = libro
            contexto_chat['libro_seleccionado'] = libro
    elif '¿te ha convencido este libro' in normalized or '¿te ha convencido' in normalized:
        pass


def list_user_chats(user: User):
    return Chat.objects.filter(user=user).order_by('-created_at')


def load_chat_history(chat: Chat):
    """Carga el historial del chat a la memoria del contexto."""
    contexto_chat["historial_conversacion"] = []
    contexto_chat["context_state"] = "IDLE"
    contexto_chat["estado"] = "NORMAL"
    contexto_chat["lista_pendiente"] = []
    contexto_chat["tipo_lista"] = ""
    contexto_chat["ultimo_libro_mencionado"] = None
    contexto_chat["ultimos_libros_encontrados"] = []
    contexto_chat["ultima_intension"] = None
    contexto_chat["esperando_respuesta"] = False
    contexto_chat["esperando_confirmacion_info"] = False
    contexto_chat["esperando_confirmacion_sinop"] = False
    contexto_chat["libro_actual"] = None
    contexto_chat["libro_seleccionado"] = None
    contexto_chat["libro_seleccionado_para_info"] = None
    contexto_chat["ultimos_libros_mostrados"] = []
    contexto_chat["ultima_respuesta_bot"] = ""
    contexto_chat["seen_books"] = chat.seen_books

    messages = list(Message.objects.filter(chat=chat).order_by('-send_at')[:10])
    messages.reverse()
    loaded = []
    for msg in messages:
        raw_text = msg.text or ""
        text = raw_text.strip()
        role = "bot" if text.lower().startswith("bot:") else "usuario"
        if text.lower().startswith("bot:"):
            text = text[4:].strip()
        elif text.lower().startswith("usuario:"):
            text = text[8:].strip()
        registrar_en_historial(role, text)
        loaded.append((role, text))

    rehydrate_context_from_loaded_history(chat, loaded)
    return loaded


def create_new_chat(user: User, get_input):
    titulo = sanitize_text(get_input("Nombre del chat: ").strip()) or "Búsqueda de libros"
    chat = Chat.objects.create(user=user, title=titulo)
    print(f"Chat creado: {titulo}")
    return chat


def guardar_mensaje_en_bd(chat: Chat, user: User, rol: str, contenido: str) -> Message:
    contenido_seguro = sanitize_text(contenido)
    its_from_user = (rol.lower() == "usuario")
    return Message.objects.create(chat=chat, its_from_user=its_from_user, text=contenido_seguro)

def chatbot(user_email=None, get_input=None):
    if get_input is None:
        def get_input(prompt: str = "") -> str:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.buffer.readline().decode('utf-8', 'ignore').strip()

    # --- INICIALIZACIÓN ---
    contexto_chat["context_state"] = "IDLE"
    libros_vistos_ids = []

    print("\n" + "="*60)
    print("BOOKBOT - RECOMENDACIONES DE LIBROS")
    print("="*60)

    if user_email is None:
        while True:
            email = get_input("Ingresa tu email: ").strip()
            if not email:
                continue
            if email.lower() in ["salir", "adios", "adiós", "adós", "bye", "exit", "chao"]:
                print("Bookbot: ¡Hasta luego!")
                return
            try:
                user = User.objects.get(email=email)
                print(f"Bienvenido, {user.username}!")
                break
            except User.DoesNotExist:
                create = get_input("Usuario no encontrado. ¿Deseas crear una cuenta nueva con este email? (sí/no): ").strip().lower()
                if create in ["sí", "si", "s", "yes", "y"]:
                    username = email.split("@")[0] if "@" in email else email
                    while True:
                        password = get_input("Ingresa una contraseña para tu nueva cuenta: ").strip()
                        if not password:
                            print("La contraseña no puede estar vacía. Por favor ingresa una contraseña válida.")
                            continue
                        confirm_password = get_input("Confirma tu contraseña: ").strip()
                        if password != confirm_password:
                            print("Las contraseñas no coinciden. Intenta de nuevo.")
                            continue
                        break
                    user = User.objects.create_user(email=email, username=username, password=password)
                    print(f"Cuenta creada. Bienvenido, {user.username}!")
                    break
                print("Ok. Ingresa otro email o escribe 'salir' para terminar.")
    else:
        user = User.objects.get(email=user_email)

    chats = list_user_chats(user)
    if chats:
        print("\nTienes chats previos:")
        for idx, existing_chat in enumerate(chats, start=1):
            message_count = Message.objects.filter(chat=existing_chat).count()
            print(f"  {idx}. {existing_chat.title} — {message_count} mensajes — Creado: {existing_chat.created_at:%Y-%m-%d}")
        print("  0. Crear un chat nuevo")

        while True:
            choice = get_input("Selecciona un chat para reanudar o 0 para crear uno nuevo: ").strip().lower()
            if choice in ["0", "n", "nuevo", "nuevo chat"]:
                chat = create_new_chat(user, get_input)
                break
            if choice.isdigit() and 1 <= int(choice) <= len(chats):
                chat = chats[int(choice) - 1]
                print(f"Reanudando chat: {chat.title}")
                loaded_history = load_chat_history(chat)
                if chat.last_genre:
                    print(f"Último género buscado en este chat: {chat.last_genre}")
                if contexto_chat.get('esperando_confirmacion_sinop'):
                    print("Parece que el chat quedó esperando tu confirmación sobre la sinopsis completa.")
                if loaded_history:
                    print("\nÚltimos mensajes de este chat:")
                    for role, text in loaded_history:
                        prefix = "Tú:" if role == "usuario" else "Bookbot:"
                        print(f"{prefix} {text}")
                break
            print("Opción inválida. Ingresa el número del chat o 0 para crear uno nuevo.")
    else:
        chat = create_new_chat(user, get_input)

    print("\n" + "="*60 + "\nPuedo buscar por Título, Autor, Género o Área.\nEscribe 'salir' para terminar.\n")

# BUCLE PRINCIPAL DE CONVERSACIÓN
    while True:
        try:
            raw_input = get_input("Tú: ")
            user_input = raw_input.strip()
            
            if not user_input or not user_input.strip():
                print("\nBookbot: No pude escuchar nada. ¿Podrías escribir tu mensaje de nuevo?")
                continue

            if user_input.lower().strip() in ["salir", "adios", "adiós", "adós", "bye", "exit", "chao"]:
                print("Bookbot: ¡Hasta luego!")
                break

            guardar_mensaje_en_bd(chat, user, "usuario", user_input)
            registrar_en_historial("usuario", user_input)

            comentario_personal = procesar_comentarios_personales(user_input)
            if comentario_personal:
                print(f"\nBookbot: {comentario_personal}\n")
                continue

            if contexto_chat.get('estado') == 'ESPERANDO_PAGINACION':
                t = user_input.lower()
                if any(keyword in t for keyword in ["más", "mas", "otros", "siguiente", "no", "ver otros", "muéstrame más", "muestrame mas"]):
                    sobrantes = contexto_chat.get('lista_pendiente', []) or []
                    tipo = contexto_chat.get('tipo_lista', 'elementos')
                    if sobrantes:
                        visibles = sobrantes[:10]
                        contexto_chat['lista_pendiente'] = sobrantes[10:]
                        lista_formateada = "\n".join([f"* {item}" for item in visibles])
                        if contexto_chat['lista_pendiente']:
                            respuesta = (
                                f"Entendido, aquí tienes otros 10 {tipo}:\n\n"
                                f"{lista_formateada}\n\n"
                                "¿Te gusta alguno o seguimos buscando?"
                            )
                        else:
                            respuesta = (
                                f"Entendido, aquí tienes otros {tipo}:\n\n"
                                f"{lista_formateada}\n\n"
                                "Esa es toda mi lista por ahora. ¿Te gustaría buscar a alguien en específico?"
                            )
                            contexto_chat['estado'] = 'NORMAL'
                        contexto_chat['context_state'] = 'IDLE'
                        guardar_mensaje_en_bd(chat, user, 'bookbot', respuesta)
                        print(f"\nBookbot: {respuesta}\n")
                        continue
                    respuesta = "Ya no tengo más en la lista. ¿Te gustaría buscar por un nombre?"
                    contexto_chat['estado'] = 'NORMAL'
                    contexto_chat['context_state'] = 'IDLE'
                    guardar_mensaje_en_bd(chat, user, 'bookbot', respuesta)
                    print(f"\nBookbot: {respuesta}\n")
                    continue
                else:
                    contexto_chat['estado'] = 'NORMAL'

            lower_input = user_input.lower()
            if "qué autores" in lower_input or "que autores" in lower_input:
                from .search import obtener_lista_autores
                lista = obtener_lista_autores()
                if lista:
                    respuesta = mostrar_lista_paginada(lista, 'autores')
                else:
                    respuesta = "Por ahora no puedo mostrar la lista, pero puedes preguntarme por cualquier autor que tengas en mente."
                guardar_mensaje_en_bd(chat, user, "bookbot", respuesta)
                print(f"\nBookbot: {respuesta}\n")
                continue

            if any(kw in lower_input for kw in ["qué géneros", "que generos", "qué generos", "generos disponibles", "qué géneros tienes", "que generos tienes", "qué tipos de libros", "que tipos de libros"]):
                from .search import obtener_lista_generos
                lista = obtener_lista_generos()
                if lista:
                    respuesta = mostrar_lista_paginada(lista, 'géneros')
                else:
                    respuesta = "Por ahora no puedo mostrar la lista de géneros, pero puedes pedirme recomendaciones por categoría."
                guardar_mensaje_en_bd(chat, user, "bookbot", respuesta)
                print(f"\nBookbot: {respuesta}\n")
                continue

            respuesta = ""
            nuevo_estado = "IDLE"
            input_norm = remover_acentos(user_input.lower())

            user_input_clean = user_input.lower().strip()
            if user_input_clean in ["si", "sí", "yes", "claro", "por supuesto", "me interesa", "me gusta", "excelente", "oki", "ok"]:
                intent = "afirmacion"
            elif user_input_clean in ["no", "nones", "para nada", "nope"]:
                intent = "negacion"
            else:
                if "recomienda" in user_input.lower() or "recomiéndame" in user_input.lower():
                    intent = "recomendacion"
                else:
                    intent = predict_intent(user_input)

            search_intents = ["consulta_avanzada", "buscar_titulo", "buscar_autor", "buscar_genero", "buscar_area", "info_libro"]

            if contexto_chat.get("context_state") == 'AWAITING_COURTESY' and intent in search_intents:
                contexto_chat["context_state"] = "IDLE"

            if contexto_chat.get("estado") == "ESPERANDO_FEEDBACK_POST_SINOP" or contexto_chat.get("context_state") == "ESPERANDO_FEEDBACK_POST_SINOP":
                if intent == "afirmacion":
                    respuesta = "¡Excelente elección! Me alegra que te haya interesado. Disfruta la lectura. ¿Hay algo más en lo que pueda ayudarte?"
                    nuevo_estado = "IDLE"
                elif intent == "negacion":
                    respuesta = "No hay problema, sigamos buscando. ¿Qué otro género o autor te gustaría explorar?"
                    nuevo_estado = "IDLE"

            if not respuesta and intent not in search_intents:
                social = respuesta_social(user_input)
                if social:
                    print(f"\nBookbot: {social}\n")
                    continue
            
            # --- DETECCIÓN E HISTORIAL DE GÉNERO ---
            inferred_genre = infer_genre_from_query(user_input)
            if inferred_genre:
                contexto_chat['current_genre'] = inferred_genre
                if 'historial_generos_backup' not in contexto_chat:
                    contexto_chat['historial_generos_backup'] = []
                if inferred_genre not in contexto_chat['historial_generos_backup']:
                    contexto_chat['historial_generos_backup'].append(inferred_genre)

                if chat.last_genre != inferred_genre:
                    chat.last_genre = inferred_genre
                    chat.save(update_fields=['last_genre'])

            # --- LÓGICA DE RECOMENDACIÓN ---
            if intent == "recomendacion" and not inferred_genre:
                from ML.handlers import handle_recommendation
                respuesta = handle_recommendation(user_input, request=None, exclude_ids=libros_vistos_ids)
                
                if contexto_chat.get("ultimos_libros_encontrados"):
                    ids_mostrados = [obtener_id_libro(l) for l in contexto_chat["ultimos_libros_encontrados"][:5]]
                    libros_vistos_ids.extend(ids_mostrados)
                nuevo_estado = 'IDLE'

            if intent == "afirmacion" and contexto_chat.get('esperando_confirmacion_sinop'):
                libro = contexto_chat.get('libro_actual') or contexto_chat.get('libro_seleccionado') or {}
                sinopsis_larga = libro.get('Sinop') or libro.get('sinop')
                if sinopsis_larga:
                    respuesta = (
                        f"Sinopsis completa de '{libro.get('titulo', 'el libro')}':\n\n"
                        f"{sinopsis_larga}\n\n"
                        "¿Qué te ha parecido esta opción? ¿Quieres que sigamos buscando otros libros?"
                    )
                else:
                    respuesta = (
                        f"Lo siento, la sinopsis detallada de '{libro.get('titulo', 'el libro')}' no está disponible en mi base de datos.\n\n"
                        "¿Qué te ha parecido esta opción? ¿Quieres que sigamos buscando otros libros?"
                    )
                contexto_chat['esperando_confirmacion_sinop'] = False
                nuevo_estado = 'ESPERANDO_FEEDBACK_POST_SINOP'
                contexto_chat['estado'] = 'ESPERANDO_FEEDBACK_POST_SINOP'
                contexto_chat['context_state'] = 'ESPERANDO_FEEDBACK_POST_SINOP'

            elif intent == "negacion" and contexto_chat.get('esperando_confirmacion_sinop'):
                respuesta = "Perfecto. ¿Hay algo más que buscas? Puedo buscar libros por título, autor, género o área."
                contexto_chat['esperando_confirmacion_sinop'] = False
                nuevo_estado = 'IDLE'

            if not respuesta and contexto_chat.get("context_state") == 'AWAITING_COURTESY' and intent not in search_intents:
                if any(word in input_norm for word in ['mal', 'triste', 'regular']):
                    respuesta = 'Lamento mucho escuchar eso. Un buen libro suele ayudar. ¿Buscamos algo de Fantasía o Romance?'
                else:
                    respuesta = '¡Me alegra mucho! ¿Qué tipo de libros te apetece explorar hoy?'
                nuevo_estado = 'IDLE'

            if not respuesta:
                respuesta = get_response(intent, user_input, request=None, exclude_ids=libros_vistos_ids)
                if contexto_chat.get("ultimos_libros_mostrados"):
                    libros_vistos_ids.extend(contexto_chat["ultimos_libros_mostrados"])

                if intent in ["como_estás", "estado_bot", "presentacion"]:
                    nuevo_estado = 'AWAITING_COURTESY'
                
                
                elif intent == "info_libro":
                    nuevo_estado = "ESPERANDO_CONFIRMACION_SINOP"
                    contexto_chat['esperando_confirmacion_sinop'] = True 
                    
                    if "¿Deseas conocer" not in respuesta:
                        respuesta += "\n\n¿Deseas conocer la sinopsis completa? (sí/no)"
                    
                    libros_encontrados = contexto_chat.get("ultimos_libros_encontrados", [])
                    libro_detectado = None
                    
                    if user_input_clean == "dame info" or "primero" in user_input_clean:
                        if libros_encontrados:
                            libro_detectado = libros_encontrados[0]
                    else:
                        for lib in libros_encontrados:
                            titulo = lib.get('titulo', '').lower()
                            if titulo and titulo in user_input_clean:
                                libro_detectado = lib
                                break
                    
                    if not libro_detectado and libros_encontrados:
                        primera_linea = respuesta.split('\n')[0].strip()
                        for lib in libros_encontrados:
                            if lib.get('titulo', '') in primera_linea:
                                libro_detectado = lib
                                break

                    if libro_detectado:
                        id_lib = obtener_id_libro(libro_detectado)
                        try:
                            from .config import supabase
                            res = supabase.table("libros").select("*").eq("id_libro", id_lib).execute()
                            if res.data:
                                contexto_chat['libro_actual'] = res.data[0]
                                contexto_chat['libro_seleccionado'] = res.data[0]
                            else:
                                contexto_chat['libro_actual'] = libro_detectado
                        except Exception as e:
                            print(f"Aviso interno (Supabase): {e}")
                            contexto_chat['libro_actual'] = libro_detectado
                

            if respuesta:
                contexto_chat["context_state"] = nuevo_estado
                guardar_mensaje_en_bd(chat, user, "bookbot", respuesta)
                print(f"\nBookbot: {respuesta}\n")
            else:
                fallback = "No estoy seguro de entender, pero puedo buscarte libros por género o autor. ¿Qué prefieres?"
                print(f"\nBookbot: {fallback}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error detectado: {e}")