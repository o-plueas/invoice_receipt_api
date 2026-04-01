

# # quotes/permissions.py
# from rest_framework import permissions

# class CanCreateQuote(permissions.BasePermission):
#     """
#     Anyone can create a quote (even unauthenticated users)
#     """
#     def has_permission(self, request, view):
#         if view.action == 'create':
#             return True
#         return request.user and request.user.is_authenticated


# class CanViewOwnQuote(permissions.BasePermission):
#     """
#     Users can only view their own quotes, admins can view all
#     """
#     def has_object_permission(self, request, view, obj):
#         if request.user.is_admin:
#             return True
        
#         if obj.user:
#             return obj.user == request.user
        
#         # For quotes created before user registration
#         return obj.email == request.user.email

















from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.is_admin:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False