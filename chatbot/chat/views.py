from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from authentication.models import User
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .permissions import MessagePermisions
from rest_framework.views import APIView, Response
from rest_framework.response import Response
from ML.chatbot import get_response, predict_intent
from ML.config import supabase

class ListPostChats(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    def get_queryset(self):
        pk_user = self.kwargs['pk']
        return Chat.objects.filter(user=pk_user)
    
    def create(self, request, *args, **kwargs):
        pk_user = self.kwargs["pk"]
        user = User.objects.get(pk=pk_user)
        Chat.objects.create(user=user, title=request.data["title"], last_genre="", seen_books=[])
        return Response(status=204)

class RetrieveModifyDeleteChat(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    
class ListMessage(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    permission_classes = [MessagePermisions]
    def get_queryset(self):
        pk_chat = self.kwargs["pk"]
        return Message.objects.filter(chat=pk_chat) 

class PostMessage(APIView):
    def post(self, request, pk):
        chat = Chat.objects.get(pk=pk)
        serializer = MessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        text_lower = serializer.validated_data["text"].lower()
        chatbot_answer = None

        if any(word in text_lower for word in ["dame info", "más info", "informacion", "sinopsis"]):
            libro_id = request.session.get('ultimo_libro_id')
            if libro_id:
                try:
                    res = supabase.table("libros").select("*").eq("id", libro_id).single().execute()
                    libro = res.data
                    # Intentamos obtener la sinopsis de varios campos posibles (info, resumen, sinopsis)
                    resumen = libro.get('info') or libro.get('resumen') or libro.get('sinopsis') or "No hay resumen disponible."
                    
                    chatbot_answer = (
                        f"**{libro['titulo']}** ({libro.get('año_publicacion', 'Desconocido')})\n\n"
                        f"**Sinopsis:** {resumen}\n\n"
                        f"¿Te gustaría buscar algo más?"
                    )
                except Exception:
                    chatbot_answer = "Lo siento, no pude obtener la información de ese libro."
            else:
                chatbot_answer = "No sé de qué libro hablamos. ¿Puedes decirme el título?"

        if chatbot_answer is None:
            retries = 0
            while retries < 3:
                intent = predict_intent(serializer.validated_data["text"])
                chatbot_answer = get_response(intent, serializer.validated_data["text"], request, [])
                if chatbot_answer: break
                retries += 1

        if chatbot_answer is None:
            return Response({"error": "El chatbot no se encuentra disponible"}, status=500)

        Message.objects.create(its_from_user=True, chat=chat, text=serializer.validated_data["text"], libro_ids=[])
        Message.objects.create(its_from_user=False, chat=chat, text=chatbot_answer, libro_ids=[])

        return Response({"msg": chatbot_answer})