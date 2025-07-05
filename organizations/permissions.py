from rest_framework import permissions
from organizations.models import Organization


class IsAdminOrSubmittedBy(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        if request.method == "POST" and request.user.is_authenticated:
            return True

        if request.user and request.user.is_staff:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        if request.user and request.user.is_staff:
            return True

        if request.user == obj.submitted_by and obj.status == "PENDING":
            return True

        return False


class IsAdminOrOrgAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        if request.method == "POST" and request.user and request.user.is_staff:
            return True

        if request.user and request.user.is_staff:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True
        if request.user and (request.user == obj.admin or request.user.is_staff):
            return True
        return False


class IsOrgAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        organization = request.kwargs.get("organization_id")
        return Organization.objects.get(id=organization).admin == request.user
