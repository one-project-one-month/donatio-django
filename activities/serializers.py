from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from organizations.serializers import SimpleOrganizationSerializer
from attachments.serializers import SimpleAttachmentSerializer
from transactions.serializers import TransactionSerializer
from .models import Activity, ActivityTransaction
from .services import create_activity, edit_activity


class ActivityTransactionSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)

    class Meta:
        model = ActivityTransaction
        fields = ["id", "transaction", "linked_at"]
        read_only_fields = fields


class ActivityDetailSerializer(serializers.ModelSerializer):
    organization = SimpleOrganizationSerializer(read_only=True)
    activity_transactions = ActivityTransactionSerializer(
        source="transaction_links", many=True, read_only=True
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "organization",
            "title",
            "description",
            "location",
            "created_at",
            "updated_at",
            "activity_transactions",
            "attachments",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "activity_transactions",
            "attachments",
            "organization",
        ]


class ActivityCreateSerializer(serializers.ModelSerializer):
    disbursement_transaction_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=True
    )
    uploaded_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "description",
            "location",
            "disbursement_transaction_ids",
            "uploaded_files",
        ]

    def create(self, validated_data):
        organization = self.context["request"].user.organization
        title = validated_data["title"]
        description = validated_data.get("description")
        location = validated_data.get("location")
        disbursement_transaction_ids = validated_data.get(
            "disbursement_transaction_ids", []
        )
        uploaded_files = validated_data.get("uploaded_files", [])

        try:
            activity = create_activity(
                org_admin_organization=organization,
                title=title,
                description=description,
                location=location,
                disbursement_transaction_ids=disbursement_transaction_ids,
                uploaded_files=uploaded_files,
            )
            return activity
        except DjangoValidationError as e:
            raise serializers.ValidationError(detail=e.message)


class ActivityEditSerializers(serializers.ModelSerializer):
    new_disbursement_transaction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "description",
            "location",
            "new_disbursement_transaction_ids",
        ]
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "location": {"required": False},
        }

    def update(self, instance, validated_data):
        user = self.context["request"].user
        title = validated_data.pop("title", None)
        description = validated_data.pop("description", None)
        location = validated_data.pop("location", None)
        new_disbursement_transaction_ids = validated_data.pop(
            "new_disbursement_transaction_ids", None
        )

        try:
            updated_activity = edit_activity(
                org_admin_user=user,
                activity_id=instance.id,
                title=title,
                description=description,
                location=location,
                new_transaction_ids=new_disbursement_transaction_ids,
            )
            return updated_activity
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                detail=e.message_dict if hasattr(e, "message_dict") else e.message
            )
        except PermissionDenied as e:
            raise serializers.ValidationError(detail=str(e), code="permission_denied")
        except Activity.DoesNotExist:
            raise serializers.ValidationError(
                detail="Activity not found.", code="not_found"
            )
        except Exception as e:
            raise serializers.ValidationError(
                detail=f"An unexpected error occurred during activity update: {str(e)}",
                code="internal_server_error",
            )
