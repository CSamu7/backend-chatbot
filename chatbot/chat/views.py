from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .permissions import MessagePermisions

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
  
class ListPostMessage(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer
  parser_classes = [FormParser,MultiPartParser, JSONParser]
  permission_classes = [MessagePermisions]

  def get_queryset(self):
    pk_chat = self.kwargs["pk"]
    return Message.objects.filter(chat=pk_chat) 


    

