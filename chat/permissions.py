from rest_framework import permissions


class IsMessageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user


class IsChatOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.donor == request.user
