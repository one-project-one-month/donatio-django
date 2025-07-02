from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "donor",
            "event",
            "amount",
            "type",
            "status",
            "review_required",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = [
            "id",
            "organization",
            "donor",
            "event",
            "type",
            "status",
            "review_required",
        ]


class UpdateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["status", "review_required"]
