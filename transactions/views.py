from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer, UpdateTransactionSerializer
from .constants import TransactionStatus
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from organizations.models import Organization
from rest_framework import serializers


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = (
        Transaction.objects.all()
        .select_related("organization", "donor", "event")
        .prefetch_related("attachments")
    )
    serializer_class = TransactionSerializer
    # filterset_fields = ['organization', 'donor', 'event', 'type', 'status', 'review_required']
    # search_fields = ['donor__name', 'event__title']
    # ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UpdateTransactionSerializer
        return TransactionSerializer

    def get_queryset(self):
        # Get the organization from the URL
        organization_pk = self.kwargs.get("organization_id")
        if organization_pk:
            return self.queryset.filter(organization__pk=organization_pk)
        return self.queryset

    def perform_create(self, serializer):
        organization_pk = self.kwargs.get("organization_id")
        organization = get_object_or_404(Organization, pk=organization_pk)
        serializer.save(
            organization=organization,
            donor=self.request.user,
        )

    def perform_destroy(self, instance):
        if (
            instance.status == TransactionStatus.APPROVED
            or instance.status == TransactionStatus.REJECTED
        ):
            raise serializers.ValidationError(
                "Cannot delete approved or rejected transaction"
            )
        return super().destroy(instance)
