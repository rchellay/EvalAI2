# Serializers adicionales para el chatbot de investigación educativa

from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer para mensajes de chat"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender', 'content', 'papers', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de chat"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    last_message = ChatMessageSerializer(read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'user_name', 'title', 'messages', 'message_count',
            'last_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'message_count', 'last_message', 'user_name', 'created_at', 'updated_at']


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar sesiones (sin mensajes completos)"""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'user_name', 'title', 'message_count',
            'last_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'message_count', 'last_message', 'user_name', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Calcular el número de mensajes"""
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """Obtener el último mensaje"""
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': last_msg.id,
                'sender': last_msg.sender,
                'content': last_msg.content[:100],  # Primeros 100 caracteres
                'timestamp': last_msg.timestamp
            }
        return None
