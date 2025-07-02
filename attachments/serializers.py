from rest_framework import serializers

from .models import Attachment


class SimpleAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "file"]


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "file", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
