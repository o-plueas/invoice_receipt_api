

# activitylog/admin.py
from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'user', 'description', 'ip_address', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('description', 'user__email', 'ip_address')
    readonly_fields = ('user', 'action_type', 'description', 'ip_address', 'user_agent', 'metadata', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('user', 'action_type', 'description')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
