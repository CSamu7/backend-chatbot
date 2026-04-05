from rest_framework import serializers

class ChatbotQuerySerializer(serializers.Serializer):
    """Serializer para consultas del chatbot"""
    query = serializers.CharField(max_length=500, help_text="Pregunta o búsqueda del usuario")
    email = serializers.EmailField(help_text="Correo del usuario (opcional)", required=False)

class ChatbotResponseSerializer(serializers.Serializer):
    """Serializer para respuestas del chatbot"""
    query = serializers.CharField()
    response = serializers.CharField()
    intent = serializers.CharField()
    timestamp = serializers.DateTimeField()