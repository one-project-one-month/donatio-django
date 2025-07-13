from django.db.models import Sum
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import OrganizationRequest, Organization
from .constants import OrganizationRequestStatus
from attachments.serializers import SimpleAttachmentSerializer
from attachments.models import Attachment
from transactions.constants import TransactionType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CreateOrganizationRequestSerializer(serializers.ModelSerializer):
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = OrganizationRequest
        fields = [
            "id",
            "organization_name",
            "type",
            "uploaded_attachments",
            "attachments",
        ]

    def create(self, validated_data):
        attachments_data = validated_data.pop("uploaded_attachments", [])
        with transaction.atomic():
            organization_request = OrganizationRequest.objects.create(**validated_data)

            for file in attachments_data:
                Attachment.objects.create(
                    content_object=organization_request, file=file
                )

        return organization_request


class UpdateOrganizationRequestSerializer(serializers.ModelSerializer):
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = OrganizationRequest
        fields = ["id", "organization_name", "type", "attachments", "status"]
        read_only_fields = ["id", "organization_name", "type", "attachments"]

    def validate_status(self, value):
        if self.instance.status == OrganizationRequestStatus.APPROVED:
            raise serializers.ValidationError("Cannot update status after approval")
        return value


class OrganizationRequestSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    attachments = serializers.SerializerMethodField(read_only=True)

    def get_attachments(self, obj):
        return SimpleAttachmentSerializer(obj.attachments.all(), many=True).data

    class Meta:
        model = OrganizationRequest
        fields = [
            "id",
            "organization_name",
            "status",
            "type",
            "submitted_by",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "attachments",
        ]


class OrganizationStatsSerializer(serializers.ModelSerializer):
    total_received_money = serializers.SerializerMethodField(read_only=True)
    total_expense = serializers.SerializerMethodField(read_only=True)
    total_current_balance = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Organization
        fields = ["total_received_money", "total_expense", "total_current_balance"]

    def get_total_received_money(self, obj):
        return (
            obj.transactions.filter(type=TransactionType.DONATION)
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

    def get_total_expense(self, obj):
        return (
            obj.transactions.filter(type=TransactionType.DISBURSEMENT)
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

    def get_total_current_balance(self, obj):
        total_received = self.get_total_received_money(obj)
        total_expense = self.get_total_expense(obj)
        return total_received - total_expense


class OrganizationSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    attachments = serializers.SerializerMethodField(read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    organization_request = OrganizationRequestSerializer(read_only=True)
    stats = serializers.SerializerMethodField(read_only=True)
    
    def get_stats(self, obj):
        return OrganizationStatsSerializer(obj).data
    
    def get_attachments(self, obj):
        return SimpleAttachmentSerializer(obj.attachments.all(), many=True).data

    class Meta:
        model = Organization
        fields = [
            "id",
            "admin",
            "name",
            "type",
            "kpay_qr_url",
            "description",
            "phone_number",
            "email",
            "organization_request",
            "additional_info",
            "created_at",
            "updated_at",
            "attachments",
            "uploaded_attachments",
            "stats"
        ]
        read_only_fields = ["name", "type", "created_at", "updated_at", "stats"]

    def update(self, instance, validated_data):
        attachments_data = validated_data.pop("uploaded_attachments", [])

        with transaction.atomic():
            # Update all other fields on the instance
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # If there are new attachments, delete old ones and create new ones
            if attachments_data:
                # Delete old attachments
                instance.attachments.all().delete()
                # Get the first attachment and link it to the organization
                instance.attachments.create(file=attachments_data[0])

            instance.save()

        return instance

    def validate_kpay_qr_url(self, value):
        if not value:
            raise serializers.ValidationError("Kpay QR URL is required")

        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required")

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must be digits")

        if value.startswith("09"):
            raise serializers.ValidationError("Phone number must not start with 09")

        if value.startswith("0"):
            raise serializers.ValidationError("Phone number must not start with 0")

        if len(value) < 8 or len(value) > 10:
            raise serializers.ValidationError("Phone number must be 8-10 digits")

        return value

    def create(self, validated_data):
        if "admin" not in validated_data and self.context["request"].user.is_staff:
            validated_data["admin"] = self.context["request"].user
        return super().create(validated_data)


class SimpleOrganizationSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    attachments = serializers.SerializerMethodField(read_only=True)

    def get_attachments(self, obj):
        return SimpleAttachmentSerializer(obj.attachments.all(), many=True).data

    class Meta:
        model = Organization
        fields = ["id", "admin", "name", "phone_number", "email", "attachments"]
