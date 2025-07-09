from chat.serializers import ChatSerializer, MessageSerializer
from chat.models import Chat, Message
from rest_framework import generics
# Create your views here.
class ListPostChats(generics.ListCreateAPIView):
  serializer_class = ChatSerializer

  def get_queryset(self):
    pk_user = self.kwargs['pk']
    return Chat.objects.filter(user=pk_user)

class RetrieveDeleteChat(generics.RetrieveDestroyAPIView):
  queryset = Chat.objects.all()
  serializer_class = ChatSerializer()

class ListPostMessage(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer()

