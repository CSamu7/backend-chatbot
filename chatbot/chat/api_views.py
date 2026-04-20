from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny
from django.utils import timezone

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from ML.chatbot import predict_intent, get_response, load_chat_history
from ML.context import contexto_chat
from authentication.models import User
from chat.models import Chat, Message
from chat.serializers import ChatSerializer, MessageSerializer


def infer_genre_from_query(query: str):
    from ML.search import extraer_criterios_avanzados
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_chats(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=HTTP_400_BAD_REQUEST)

    chats = Chat.objects.filter(user=user).order_by('-created_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chat_history(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"error": "Chat no encontrado"}, status=HTTP_400_BAD_REQUEST)

    messages = Message.objects.filter(chat=chat).order_by('send_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_api(request):
    """
    API REST para el chatbot
    
    POST /api/chatbot/
    {
        "query": "Busco libros de terror de menos de 300 páginas",
        "email": "usuario@example.com"
    }
    
    Response:
    {
        "query": "Busco libros de terror de menos de 300 páginas",
        "response": "Aquí están los libros que encontré...",
        "intent": "consulta_avanzada",
        "timestamp": "2026-03-10T21:36:50Z"
    }
    """
    try:
        query = request.data.get('query', '').strip()
        email = request.data.get('email', '').strip()
        
        if not query:
            return Response(
                {"error": "El parámetro 'query' es requerido"},
                status=HTTP_400_BAD_REQUEST
            )
        
       
        chat = None
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
                chat = Chat.objects.filter(user=user).order_by('-created_at').first()
                if not chat:
                    chat = Chat.objects.create(user=user, title='Chat via API')
                
                
                load_chat_history(chat)
                request.chat = chat
            except User.DoesNotExist:
                pass
        
    
        intent = predict_intent(query)
        
    
        response = get_response(intent, query, request=request)
        
        
        if chat and user:
            # Guardar mensajes
            Message.objects.create(chat=chat, its_from_user=True, text=f"Usuario: {query}")
            Message.objects.create(
                chat=chat,
                its_from_user=False,
                text=f"Bot: {response}",
                libro_ids=contexto_chat.get('ultimos_libros_mostrados', []) or []
            )

            # Guardar el género (primero intenta el que se detectó en handlers, luego el de la query actual)
            genre = contexto_chat.get('ultimo_genero_exitoso') or infer_genre_from_query(query)
            if genre:
                chat.last_genre = genre
           
            seen_books = contexto_chat.get('seen_books', [])
            chat.seen_books = seen_books
            chat.save(update_fields=['last_genre', 'seen_books'])

        
        return Response({
            "query": query,
            "response": response,
            "intent": intent,
            "timestamp": timezone.now().isoformat()
        }, status=HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Error procesando la solicitud: {str(e)}"},
            status=HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_info(request):
    """
    Información sobre los tipos de consultas soportadas por el bot
    """
    return Response({
        "name": "Bookbot de Recomendaciones de Libros",
        "version": "2.0",
        "supported_intents": {
            "saludo": "Saludos al chatbot",
            "despedida": "Despedirse del chatbot",
            "buscar_titulo": "Buscar libros por título",
            "buscar_autor": "Buscar libros por autor",
            "buscar_genero": "Buscar libros por género",
            "buscar_area": "Buscar libros por área temática",
            "recomendacion": "Obtener recomendaciones",
            "consulta_avanzada": "Búsqueda avanzada con múltiples criterios",
            "info": "Obtener información detallada de un libro",
            "agradecer": "Expresar gratitud"
        },
        "consulta_avanzada_ejemplos": [
            "Busco libro de no más de 300 páginas, de género suspenso y terror",
            "Recomiéndame un libro de Stephen King de al menos 300 páginas",
            "Libros de menos de 200 páginas de ciencia ficción",
            "Busco libros de drama de al menos 500 páginas"
        ],
        "endpoint": "/api/chatbot/"
    })
