from rest_framework import serializers
from .models import Notification
from organizations.models import Organization
from django.contrib.auth import get_user_model


class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "highlight",
            "message",
            "type",
            "is_read",
            "source_object",
        ]

    source_object = serializers.SerializerMethodField()

    def get_source_object(self, obj):
        if not obj.source_object:
            return None

        if isinstance(obj.source_object, Organization):
            return {
                "type": "organization",
                "id": str(obj.source_object.pk),
                "name": obj.source_object.name,
            }
        elif isinstance(obj.source_object, get_user_model()):
            return {
                "type": "user",
                "id": str(obj.source_object.pk),
                "username": obj.source_object.username,
            }

        return str(obj.source_object)
