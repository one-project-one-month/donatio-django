from rest_framework import permissions
from organizations.models import Organization


class IsOrgAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        organization_id = view.kwargs.get("organization_pk")
        return Organization.objects.get(id=organization_id).admin == request.user
