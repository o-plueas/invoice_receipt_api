

# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'invoice_number', 'amount', 'payment_method', 'status_badge', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'invoice__invoice_number', 'user__email')
    readonly_fields = ('transaction_id', 'created_at', 'completed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('invoice', 'user', 'amount')
        }),
        ('Method & Status', {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
        ('Gateway Details', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def invoice_number(self, obj):
        return obj.invoice.invoice_number
    invoice_number.short_description = 'Invoice'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'completed': '#10b981',
            'failed': '#ef4444',
            'refunded': '#6b7280',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_status, '#6b7280'),
            obj.get_payment_status_display()
        )
    status_badge.short_description = 'Status'
