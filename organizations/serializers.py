from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OrganizationRequest, Organization
from .constants import OrganizationRequestStatus
from attachments.serializers import SimpleAttachmentSerializer
from attachments.models import Attachment
from django.db import transaction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CreateOrganizationRequestSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = OrganizationRequest
        fields = ["organization_name", "attachments"]

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        with transaction.atomic():
            organization_request = OrganizationRequest.objects.create(**validated_data)

            for file in attachments_data:
                Attachment.objects.create(
                    content_object=organization_request, file=file
                )

        return organization_request


class UpdateOrganizationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRequest
        fields = ["status"]

    def validate_status(self, value):
        if self.instance.status == OrganizationRequestStatus.APPROVED:
            raise serializers.ValidationError("Cannot update status after approval")
        return value


class OrganizationRequestSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    attachments = SimpleAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = OrganizationRequest
        fields = [
            "id",
            "organization_name",
            "status",
            "submitted_by",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "attachments",
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="admin", write_only=True, required=False
    )

    organization_request = OrganizationRequestSerializer(read_only=True)
    organization_request_id = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationRequest.objects.all(), source=""
    )

    class Meta:
        model = Organization
        fields = [
            "id",
            "admin",
            "admin_id",
            "organization_name",
            "description",
            "phone_number",
            "email",
            "additional_info",
            "organization_request",
            "organization_request_id",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        if "admin" not in validated_data and self.context["request"].user.is_staff:
            validated_data["admin"] = self.context["request"].user
        return super().create(validated_data)
