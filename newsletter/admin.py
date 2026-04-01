from django.contrib import admin
from .models import Newsletter 
from django.utils.html import format_html 

# Register your models here.
@admin.register(Newsletter)

class NewsletterAdmin(admin.ModelAdmin):
    list_diplay = ('email', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at')

    fieldsets = (
        ('Newsletter Infor', {
            'fields': ('email')
        }), 
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'saved': '#10b981',
          
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['save_newsletter', 'reject_newsletter']


    def save_newsletter(self, request, queryset):
        updated = queryset.update(status='saved')
        self.message_user(request, f'{updated} email saved succesfully.')
    save_newsletter.short_description = 'Saved selected email'
    
    def reject_newsletter(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} email rejected succesfully.')

    reject_newsletter.short_description = 'Rejected selected email'