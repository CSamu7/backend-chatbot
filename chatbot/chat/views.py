from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
from .permissions import ChatPermissions

class ListPostChats(generics.ListCreateAPIView):
  serializer_class = ChatSerializer
  permission_classes = [ChatPermissions]

  def get_queryset(self):
    pk_user = self.kwargs['pk']
    return Chat.objects.filter(user=pk_user)
  
class RetrieveDeleteChat(generics.RetrieveDestroyAPIView):
  queryset = Chat.objects.all()
  serializer_class = ChatSerializer()
  permission_classes = [ChatPermissions]

class ListPostMessage(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer

  def get_queryset(self):
    pk_chat = self.kwargs["pk"]
    return Message.objects.filter(chat=pk_chat)

