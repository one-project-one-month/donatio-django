from rest_framework import permissions
from organizations.models import Organization

class IsOrgAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id")
        return Organization.objects.filter(pk=organization_id, admin=request.user).exists()

    def has_object_permission(self, request, view, obj):
        return obj.organization.admin == request.user

