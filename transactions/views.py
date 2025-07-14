from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer, UpdateTransactionSerializer
from .constants import TransactionStatus, TransactionType
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from organizations.models import Organization
from rest_framework import serializers
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from core.permissions import IsOrgAdmin
from rest_framework.views import APIView


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = (
        Transaction.objects.all()
        .select_related("organization", "actor", "event")
        .prefetch_related("attachments")
    )
    serializer_class = TransactionSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["title"]
    filterset_fields = ["type", "status", "event", "review_required"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    def get_permissions(self):
        # To create user can be org admin or donor
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UpdateTransactionSerializer
        return TransactionSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        context["actor"] = self.request.user
        
        organization_pk = self.kwargs.get("organization_id")
        self.organization = get_object_or_404(Organization, pk=organization_pk)
        context["organization"] = self.organization
        
        return context

    def get_queryset(self):
        # Get the organization from the URL
        organization_pk = self.kwargs.get("organization_id")
        return self.queryset.filter(organization__pk=organization_pk)

    def perform_create(self, serializer):
        
        # Access validated data safely
        transaction_type = serializer.validated_data.get("type")
        amount = serializer.validated_data.get("amount")
        # Auto-set title if donation and no title provided
        if transaction_type == TransactionType.DONATION:
            serializer.validated_data["title"] = f"{self.request.user.username} donated {amount}"
            
        serializer.save(
            organization=self.organization,
            actor=self.request.user,
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


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(
            actor=request.user, type=TransactionType.DONATION
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
