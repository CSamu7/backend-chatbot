from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from authentication.models import User
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .permissions import MessagePermisions
from rest_framework.views import APIView, Response
from rest_framework.response import Response
from ML.core import get_response, predict_intent
from ML.config import supabase

class ListPostChats(generics.ListCreateAPIView):
  serializer_class = ChatSerializer

  def get_queryset(self):
    pk_user = self.kwargs['pk']
    return Chat.objects.filter(user=pk_user)
  
  def create(self, request, *args, **kwargs):
    pk_user = self.kwargs["pk"]
    user = User.objects.get(pk = pk_user)

    Chat.objects.create(user=user, title=request.data["title"], last_genre = "", seen_books = [])

    return Response(status=204)
  


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
      text_lower = serializer.validated_data["text"].lower()
      
      intent = predict_intent(serializer.validated_data["text"], request.session)
      chatbot_answer = get_response(intent, serializer.validated_data["text"], request, [])

      if chatbot_answer is not None: 
         break

      retries += 1

    if retries >= 3:
  
      return Response({"error": "El chatbot no se encuentra disponible"}, status=500)

    chat = Chat.objects.get(pk = pk)
    user_msg = Message(its_from_user = True, chat = chat, text = serializer.validated_data["text"], libro_ids = [])
    chatbot_msg = Message(chat = chat, text = chatbot_answer, libro_ids = [])

    user_msg.save()
    chatbot_msg.save()

    return Response({"msg": chatbot_answer})