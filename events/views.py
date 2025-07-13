from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from events.models import Event
from events.serializers import EventSerializer
from events.constants import EventStatusChoices
from organizations.models import Organization
from core.permissions import IsOrgAdmin
from organizations.paginations import CommonPagination


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    pagination_class = CommonPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["title"]
    filterset_fields = ["status"]
    http_method_names = ["get", "patch", "post"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        if self.action == "list":
            return Event.objects.filter(organization=self.kwargs.get("organization_pk"))
        return super().get_queryset()

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization, id=self.kwargs.get("organization_pk")
        )
        serializer.save(organization=organization, start_date=timezone.now())


class EventListViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination
    http_method_names = ["get"]

    def get_queryset(self):
        if self.action == "list":
            return Event.objects.filter(status=EventStatusChoices.OPEN)
        return Event.objects.all()
