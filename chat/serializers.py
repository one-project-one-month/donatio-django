from rest_framework import serializers
from .models import Chat, ChatMessage
from accounts.serializers import CustomUserDetailsSerializer


class ChatSerializer(serializers.ModelSerializer):
    donor = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"
