from rest_framework import serializers
from events.models import Event
from organizations.serializers import SimpleOrganizationSerializer
from attachments.serializers import SimpleAttachmentSerializer
from attachments.models import Attachment
from django.db import transaction


class EventSerializer(serializers.ModelSerializer):
    organization = SimpleOrganizationSerializer(read_only=True)
    attachments = SimpleAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "organization",
            "title",
            "status",
            "description",
            "target_amount",
            "attachments",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["start_date"]

    def create(self, validated_data):
        attachments = validated_data.pop("uploaded_attachments", [])
        with transaction.atomic():
            event = Event.objects.create(**validated_data)
            for attachment in attachments:
                Attachment.objects.create(content_object=event, file=attachment)

            return event
        
class SimpleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "organization",
            "title",
            "status",
        ]
