from rest_framework import serializers
from .models import Chat, Message
from authentication.serializers import UsersSerializer

class ChatSerializer(serializers.ModelSerializer):
  class Meta:
    model = Chat
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    fields = ["id", "title", "created_at", "user"]

class MessageSerializer(serializers.ModelSerializer):
  user = UsersSerializer()

  class Meta:
    model = Message
    fields = ["user", "text", "send_at"]

  def validate_text(self, text = str):
    if len(text) <= 0:
      raise serializers.ValidationError("No puedes enviar un mensaje vacio")
    
    return text
