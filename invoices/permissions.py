
# invoices/permissions.py
from rest_framework import permissions

class CanViewInvoice(permissions.BasePermission):
    """
    Users can view their own invoices, admins can view all
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.user == request.user


class CanCreateInvoice(permissions.BasePermission):
    """
    Only admins can create invoices
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

