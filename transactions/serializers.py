from rest_framework import serializers
from .models import Transaction
from attachments.serializers import SimpleAttachmentSerializer
from django.db import transaction as db_transaction
from .constants import TransactionType, TransactionStatus
from organizations.serializers import SimpleOrganizationSerializer
from accounts.serializers import SimpleUserSerializer
from events.serializers import SimpleEventSerializer


class TransactionSerializer(serializers.ModelSerializer):
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)
    organization = SimpleOrganizationSerializer(read_only=True)
    actor = SimpleUserSerializer(read_only=True)
    event = SimpleEventSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "actor",
            "event",
            "title",
            "amount",
            "type",
            "status",
            "review_required",
            "created_at",
            "updated_at",
            "attachments",
            "uploaded_attachments",
        ]
        read_only_fields = [
            "id",
            "organization",
            "actor",
            "status",
            "uploaded_attachments",
            "attachments",
            "review_required",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        attachments_data = validated_data.pop("uploaded_attachments", [])
        with db_transaction.atomic():
            transaction = Transaction.objects.create(**validated_data)
            if validated_data["type"] == TransactionType.DONATION:
                # Add the first attachment to the transaction
                transaction.attachments.create(file=attachments_data[0])
            elif validated_data["type"] == TransactionType.DISBURSEMENT:
                # Add all attachments to the transaction
                for file in attachments_data:
                    transaction.attachments.create(file=file)
            else:
                raise serializers.ValidationError("Invalid transaction type")
        return transaction

    def validate(self, attrs):
        actor = self.context.get("actor")
        organization = self.context.get("organization")

        if attrs["type"] == TransactionType.DISBURSEMENT:
            if organization.admin != actor:
                raise serializers.ValidationError("You are not authorized to create disbursement transactions for this organization.")

            if attrs.get("event") is not None:
                raise serializers.ValidationError("Disbursement transactions cannot be associated with an event.")

            title = attrs.get("title")
            if not title or title.strip() == "":
                raise serializers.ValidationError("Title is required for disbursements.")

        elif attrs["type"] == TransactionType.DONATION:
            if not organization.kpay_qr_url or not organization.phone_number:
                raise serializers.ValidationError("Organization is not set up properly yet to accept donations.")

        return super().validate(attrs)



class UpdateTransactionSerializer(serializers.ModelSerializer):
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)
    organization = SimpleOrganizationSerializer(read_only=True)
    actor = SimpleUserSerializer(read_only=True)
    event = SimpleEventSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "actor",
            "event",
            "title",
            "amount",
            "type",
            "status",
            "review_required",
            "attachments",
            "uploaded_attachments",
        ]
        read_only_fields = [
            "id",
            "organization",
            "actor",
            "event",
            "amount",
            "type",
            "attachments",
        ]

    def update(self, instance, validated_data):
        attachments_data = validated_data.pop("uploaded_attachments", [])
        with db_transaction.atomic():
            # For Disbursements, we need to delete all attachments and add new ones
            # For Donations, we need to delete the first attachment and add a new one

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if attachments_data:
                if instance.type == TransactionType.DISBURSEMENT:
                    instance.attachments.all().delete()
                    for file in attachments_data:
                        instance.attachments.create(file=file)
                elif instance.type == TransactionType.DONATION:
                    instance.attachments.all().delete()
                    instance.attachments.create(file=attachments_data[0])

            instance.save()
        return instance

    def validate(self, attrs):
        # If the status is approved, we cannot update it
        if self.instance and self.instance.status == TransactionStatus.APPROVED:
            raise serializers.ValidationError("Cannot update status after approval")

        # If the status is rejected, we cannot update it
        if self.instance and self.instance.status == TransactionStatus.REJECTED:
            raise serializers.ValidationError("Cannot update status after rejection")

        # If the status is pending, we can update it

        return super().validate(attrs)
