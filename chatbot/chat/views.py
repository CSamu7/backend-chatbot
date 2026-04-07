from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .permissions import MessagePermisions
from rest_framework.views import APIView, Response

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
  def create(self, request):
    #validate message
    serializer = MessageSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.error_messages)

    retries = 0

    while retries < 3:
      # enviar al chatbot con el mensaje
      # calling chatbot

      # if request is successful, then break.
      retries += 1


    if retries >= 3:
    #after 3 retries and no message sent, return 500.
      return Response({"error": "El chatbot no se encuentra disponible"}, status=500)

    user_msg = Message.objects.create(serializer.data)
    chatbot_msg = Message.objects.create(serializer.data)
    #save both messages in the database.

    user_msg.save()
    chatbot_msg.save()
    #return chatbot message.

    return Response({"msg": chatbot_msg})
