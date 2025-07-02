from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from .models import OrganizationRequest, Organization
from .serializers import OrganizationRequestSerializer, OrganizationSerializer
from .permissions import IsAdminOrSubmittedBy, IsAdminOrOrgAdmin
from .constants import OrganizationRequestStatus


class OrganizationRequestViewSet(viewsets.ModelViewSet):
    queryset = OrganizationRequest.objects.all().order_by('-created_at')
    serializer_class = OrganizationRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSubmittedBy]  

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'submitted_by__username']
    search_fields = ['organization_name']
    ordering_fields = ['created_at', 'organization_name', 'status']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):

        organization_request = self.get_object()
        if organization_request.status == OrganizationRequestStatus.PENDING:
            organization_request.status = OrganizationRequestStatus.APPROVED
            organization_request.approved_by = request.user
            organization_request.approved_at = timezone.now()
            organization_request.save()
            return Response(self.get_serializer(organization_request).data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Organization request is not in PENDING status or already approved."},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        organization_request = self.get_object()
        if organization_request.status == OrganizationRequestStatus.PENDING:
            organization_request.status = OrganizationRequestStatus.REJECTED
            organization_request.approved_by = request.user
            organization_request.approved_at = timezone.now()
            organization_request.save()
            return Response(self.get_serializer(organization_request).data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Organization request is not in PENDING status or already rejected."},
            status=status.HTTP_400_BAD_REQUEST
        )

class OrganizationViewSet(viewsets.ModelViewSet):

    queryset = Organization.objects.all().order_by('-created_at')
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOrgAdmin]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['admin__username', 'organization_request__status']
    search_fields = ['organization_name']
    ordering_fields = ['created_at', 'organization_name']

    def perform_create(self, serializer):
        organization_request = serializer.validated_data.get('organizaiton_request')
        if organization_request and organization_request.status != OrganizationRequestStatus.APPROVED:
            raise serializers.ValidationError({"organization_request" : "The linked organization request must be approved."})

        if not serializer.validated_data.get('admin') and self.request.user.is_staff:
            serializer.save(admin=self.request.user)
        else:
            serializer.save()