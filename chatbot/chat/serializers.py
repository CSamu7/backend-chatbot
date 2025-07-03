from rest_framework import serializers
from .models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
  class Meta:
    model = Chat
    fields = [
      "id", 
      "user", 
      "title", 
      "created_at"
    ]
    

class MessageSerializer(Message):
  class Meta:
    model = Message
    fields = ["id", "chat", "user", "content", "send_at"]