from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers
from django.utils import timezone

from .models import OrganizationRequest, Organization
from .serializers import (
    OrganizationRequestSerializer,
    OrganizationSerializer,
    CreateOrganizationRequestSerializer,
    UpdateOrganizationRequestSerializer,
)
from .permissions import IsAdminOrOrgAdmin
from .constants import OrganizationRequestStatus
from rest_framework.parsers import MultiPartParser, FormParser


class OrganizationRequestViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = OrganizationRequest.objects.all().order_by("-created_at")
    serializer_class = OrganizationRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backend = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "submitted_by__username"]
    search_fields = ["organization_name"]
    ordering_fields = ["created_at", "organization_name", "status"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrganizationRequestSerializer
        elif self.action in ["update", "partial_update"]:
            return UpdateOrganizationRequestSerializer
        return OrganizationRequestSerializer

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(approved_by=self.request.user, approved_at=timezone.now())


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all().order_by("-created_at")
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOrgAdmin]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["admin__username", "organization_request__status"]
    search_fields = ["organization_name"]
    ordering_fields = ["created_at", "organization_name"]

    def perform_create(self, serializer):
        organization_request = serializer.validated_data.get("organization_request")
        if (
            organization_request
            and organization_request.status != OrganizationRequestStatus.APPROVED
        ):
            raise serializers.ValidationError(
                {
                    "organization_request": "The linked organization request must be approved."
                }
            )

        if not serializer.validated_data.get("admin") and self.request.user.is_staff:
            serializer.save(admin=self.request.user)
        else:
            serializer.save()
