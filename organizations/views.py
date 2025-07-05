from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from .models import OrganizationRequest, Organization
from .serializers import (
    OrganizationRequestSerializer,
    OrganizationSerializer,
    CreateOrganizationRequestSerializer,
    UpdateOrganizationRequestSerializer,
)
from .permissions import IsAdminOrOrgAdmin, IsOrgAdmin
from rest_framework.parsers import MultiPartParser, FormParser
from attachments.models import Attachment
from django.shortcuts import get_object_or_404
from chat.models import Chat
from chat.serializers import ChatSerializer


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
    # pagination_class = CommonPagination
    http_method_names = ["get", "put", "patch", "delete"]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["admin__username", "organization_request__status"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]

    def perform_update(self, serializer):
        # Organization has more than one attachment in attachments field
        if serializer.validated_data.get("attachments"):
            # Check if there are old
            if serializer.validated_data["attachments"]:
                # Delete old linked attachments of the organization
                Attachment.objects.filter(organization=serializer.instance).delete()

        return super().perform_update(serializer)


class OrganizationChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "list":
            return Chat.objects.filter(organization=self.kwargs.get("organization_pk"))
        return Chat.objects.all()

    def create(self, request, *args, **kwargs):
        organization = get_object_or_404(
            Organization, id=self.kwargs.get("organization_pk")
        )

        # get or start new chat
        chat, created = Chat.objects.get_or_create(
            donor=request.user,
            organization=organization,
            defaults={"created_at": timezone.now()},
        )

        return Response(
            {"created": created, "chat_id": chat.id}, status=status.HTTP_200_OK
        )
