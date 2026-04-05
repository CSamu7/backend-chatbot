from rest_framework import serializers
from .models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

  class Meta:
    model = Chat
    fields = ["id", "title", "created_at", "user", "last_genre"]

class MessageSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
  chat = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = Message
    fields = ["user", "text", "send_at", "chat"]

  def validate_text(self, text = str):
    if len(text) <= 0:
      raise serializers.ValidationError("No puedes enviar un mensaje vacio")
    
    return text
