from rest_framework import serializers
from .models import Transaction
from attachments.serializers import SimpleAttachmentSerializer
from django.db import transaction as db_transaction
from .constants import TransactionType, TransactionStatus


class TransactionSerializer(serializers.ModelSerializer):
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "donor",
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
            "donor",
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
        # If the transaction is a disbursement and the event is not None, raise an error
        if (attrs["type"] == TransactionType.DISBURSEMENT) and (
            attrs["event"] is not None
        ):
            raise serializers.ValidationError(
                "Disbursement transaction cannot be associated with an event"
            )

        # If the transaction is a donation and the title is not set, set the title to the donor's username and the amount
        if (attrs["type"] == TransactionType.DONATION) and (attrs["title"] is None):
            attrs["title"] = f"{attrs['donor'].username} donated {attrs['amount']}"

        return super().validate(attrs)


class UpdateTransactionSerializer(serializers.ModelSerializer):
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "donor",
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
            "donor",
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
