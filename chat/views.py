from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Chat, ChatMessage
from .serializers import (
    ChatSerializer,
    ChatMessageSerializer,
    UpdateChatMessageSerializer,
)
from .permissions import IsChatOwner, IsMessageOwner


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    http_method_names = ["get", "delete"]
    pagination_class = None

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated()]

        return [permissions.IsAuthenticated(), IsChatOwner()]

    def get_queryset(self):
        if self.action == "list":
            return Chat.objects.filter(donor=self.request.user)

        return Chat.objects.all()

    # To retrieve all the messages of a chat (message history)
    @action(detail=True, methods=["get"], url_path="messages")
    def get_messages(self, request, pk=None):
        messages = ChatMessage.objects.filter(chat=pk)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsMessageOwner]
    http_method_names = ["put", "delete"]

    def get_serializer_class(self):
        if self.action == "update":
            return UpdateChatMessageSerializer
        return super().get_serializer_class()
