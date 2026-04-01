from rest_framework import permissions 

class Is_Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.is_authenticated and request.is_admin 
    

class IsOwnerorAddmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.is_admin:
            return True
        
        # check if user owns object 

        if hasattr(obj, 'user'):
            return obj.user == request.user 
        
        return False 