# accounts/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can access everything
        if request.user.is_admin:
            return True
        
        # Check if object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsOwnerOrAdminQuote(permissions.BasePermission):
    """
    Custom permission for quotes - anonymous users can
      create, owners/admins can view
    """
    def has_permission(self, request, view):
        # Allow anonymous POST for quote creation
        if view.action == 'create':
            return True
        
        # Require authentication for other actions
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admins can do everything
        if request.user.is_admin:
            return True
        
        # Users can view their own quotes
        if obj.user:
            return obj.user == request.user
        
        # Check if email matches for anonymous quotes
        if hasattr(obj, 'email'):
            return obj.email == request.user.email
        
        return False

