from rest_framework import serializers
from .models import Chat, Message
from authentication.serializers import UsersSerializer

class ChatSerializer(serializers.ModelSerializer):
  class Meta:
    model = Chat
    fields = ["id", "title", "created_at"]

class MessageSerializer(serializers.ModelSerializer):
  user = UsersSerializer()

  class Meta:
    model = Message
    fields = ["user", "text", "send_at"]

  def validate_text(self, text = str):
    if len(text) <= 0:
      raise serializers.ValidationError("No puedes enviar un mensaje vacio")
    
    return text
