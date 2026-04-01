
# activitylog/models.py
from django.db import models
from accounts.models import User

class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('quote_created', 'Quote Created'),
        ('quote_approved', 'Quote Approved'),
        ('quote_rejected', 'Quote Rejected'),
        ('invoice_created', 'Invoice Created'),
        ('invoice_paid', 'Invoice Paid'),
        ('receipt_generated', 'Receipt Generated'),
        ('user_registered', 'User Registered'),
        ('user_login', 'User Login'),
        ('settings_updated', 'Settings Updated'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.user.email if self.user else 'System'}"
