

# receipts/permissions.py
from rest_framework import permissions

class CanViewReceipt(permissions.BasePermission):
    """
    Users can view their own receipts, admins can view all
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.invoice.user == request.user