from django.contrib import admin

# Register your models here.

# quotes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Quote

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'name', 'email', 'service_type', 'status_badge', 'created_at')
    list_filter = ('status', 'service_type', 'created_at')
    search_fields = ('reference_number', 'name', 'email', 'phone', 'message')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'pdf_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('reference_number', 'user', 'status')
        }),
        ('Contact Details', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Service Details', {
            'fields': ('service_type', 'message', 'attachment')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
        ('Documents', {
            'fields': ('pdf_file', 'pdf_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'approved': '#10b981',
            'rejected': '#ef4444',
            'converted': '#3b82f6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">View PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF generated"
    pdf_preview.short_description = 'PDF Preview'
    
    actions = ['approve_quotes', 'reject_quotes']
    
    def approve_quotes(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} quote(s) approved successfully.')
    approve_quotes.short_description = 'Approve selected quotes'
    
    def reject_quotes(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} quote(s) rejected.')
    reject_quotes.short_description = 'Reject selected quotes'

