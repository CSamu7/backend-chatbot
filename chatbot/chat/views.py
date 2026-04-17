from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .permissions import MessagePermisions
from rest_framework.views import APIView, Response
from rest_framework.response import Response
from ML.chatbot import get_response, predict_intent
from ML.config import supabase

class ListChats(generics.ListAPIView):
  serializer_class = ChatSerializer

  def get_queryset(self):
    pk_user = self.kwargs['pk']
    return Chat.objects.filter(user=pk_user)
  
class PostChat(generics.CreateAPIView):
  parser_classes = [FormParser,MultiPartParser, JSONParser]
  serializer_class = ChatSerializer

class RetrieveModifyDeleteChat(generics.RetrieveUpdateDestroyAPIView):
  queryset = Chat.objects.all()
  serializer_class = ChatSerializer
  
class ListMessage(generics.ListAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer
  parser_classes = [FormParser,MultiPartParser, JSONParser]
  permission_classes = [MessagePermisions]

  def get_queryset(self):
    pk_chat = self.kwargs["pk"]
    return Message.objects.filter(chat=pk_chat) 

class PostMessage(APIView):
  def post(self, request, pk):
    #validate message
    serializer = MessageSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.error_messages)

    retries = 0

    while retries < 3:
  # 1. Detectar si el usuario pide info del libro actual
      text_lower = serializer.validated_data["text"].lower()
      
      #Demasiada información...
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
      intent = predict_intent(serializer.validated_data["text"])
      #def get_response(intent: str, user_input: str, request=None, exclude_ids: list = None) -> str:
      chatbot_answer = get_response(intent, serializer.validated_data["text"], request, [])

      if chatbot_answer is not None: 
         break

      retries += 1

    if retries >= 3:
    #after 3 retries and no message sent, return 500.
      return Response({"error": "El chatbot no se encuentra disponible"}, status=500)

    chat = Chat.objects.get(pk = pk)
    user_msg = Message(its_from_user = True, chat = chat, text = serializer.validated_data["text"], libro_ids = [])
    chatbot_msg = Message(chat = chat, text = chatbot_answer, libro_ids = [])

    user_msg.save()
    chatbot_msg.save()

    return Response({"msg": chatbot_answer})
