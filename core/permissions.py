"""
Reusable custom permission classes.
"""
from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission to only allow owners of an object to access or edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False
