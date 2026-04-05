from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
from .permissions import ChatPermissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ML.chatbot import get_response, predict_intent
from ML.config import supabase
from authentication.models import User

class ListPostChats(generics.ListCreateAPIView):
  serializer_class = ChatSerializer
  permission_classes = [ChatPermissions]
  authentication_classes = [TokenAuthentication]

  def get_queryset(self):
    pk_user = self.kwargs['pk']
    return Chat.objects.filter(user=pk_user)
  
class RetrieveDeleteChat(generics.RetrieveDestroyAPIView):
  queryset = Chat.objects.all()
  serializer_class = ChatSerializer()
  permission_classes = [ChatPermissions]
  authentication_classes = [TokenAuthentication]
  
class ListPostMessage(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer

  def get_queryset(self):
    pk_chat = self.kwargs["pk"]
    return Message.objects.filter(chat=pk_chat)

class ChatbotAPIView(APIView):
    """API para interactuar con el chatbot ML"""
    def post(self, request):
        email = request.data.get('email')
        text = request.data.get('text')
        if not email or not text:
            return Response({'error': 'Faltan parámetros'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # 1. Detectar si el usuario pide info del libro actual
        text_lower = text.lower()
        if "dame info" in text_lower or "más info" in text_lower or "informacion" in text_lower or "sinopsis" in text_lower:
            libro_id = request.session.get('ultimo_libro_id')
            if libro_id:
                try:
                    res = supabase.table("libros").select("*").eq("id", libro_id).single().execute()
                    libro = res.data
                    respuesta = f"**{libro['titulo']}** ({libro.get('año_publicacion', 'Desconocido')})\n\n**Sinopsis:** {libro.get('info', 'No hay resumen disponible.')}\n\n¿Te gustaría buscar algo más?"
                    return Response({'respuesta': respuesta})
                except Exception as e:
                    return Response({'respuesta': 'Lo siento, no pude obtener la información de ese libro.'})
            else:
                return Response({'respuesta': "No sé de qué libro hablamos. ¿Puedes decirme el título?"})
        
        # 2. Si es una búsqueda normal
        intent = predict_intent(text)
        respuesta = get_response(intent, text, request, user)
        return Response({'respuesta': respuesta})

