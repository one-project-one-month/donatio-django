from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.filters import SearchFilter

from activities.models import Activity
from organizations.models import Organization
from .serializers import ActivityDetailSerializer
from .permissions import IsOrgAdmin

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityDetailSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['title']
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        if self.action == "list":
            return Activity.objects.filter(organization=self.kwargs.get("organization_pk"))
        return super().get_queryset()
    
    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, id=self.kwargs.get("organization_pk"))
        serializer.save(organization=organization)
        
class ActivityListViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['title']
    http_method_names = ['get']