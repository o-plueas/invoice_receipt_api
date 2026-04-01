# receipts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Receipt, ReceiptLineItem

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 
        'invoice_link', 
        'customer_name', 
        'amount_paid', 
        'payment_method_badge',
        'payment_date',
        'created_at'
    )
    list_filter = ('payment_method', 'created_at', 'payment_date')
    search_fields = (
        'receipt_number', 
        'invoice__invoice_number', 
        'invoice__quote__name',
        'transaction_id'
    )
    readonly_fields = (
        'receipt_number', 
        'invoice', 
        'amount_paid',
        'customer_name',
        'customer_email', 
        'customer_phone',
        'service_type',
        'payment_date',
        'created_at',
        'pdf_preview'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Receipt Information', {
            'fields': ('receipt_number', 'invoice', 'payment_date')
        }),
        ('Customer Information (From Invoice)', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'service_type'),
            'classes': ('collapse',)
        }),
        ('Payment Details', {
            'fields': ('amount_paid', 'payment_method', 'transaction_id')
        }),
        ('Additional Info', {
            'fields': ('notes', 'pdf_file', 'pdf_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_link(self, obj):
        return format_html(
            '<a href="/admin/invoices/invoice/{}/change/">{}</a>',
            obj.invoice.id,
            obj.invoice.invoice_number
        )
    invoice_link.short_description = 'Invoice'
    
    def payment_method_badge(self, obj):
        colors = {
            'cash': '#10b981',
            'bank_transfer': '#3b82f6',
            'card': '#8b5cf6',
            'check': '#f59e0b',
            'online': '#06b6d4',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_method, '#6b7280'),
            obj.get_payment_method_display()
        )
    payment_method_badge.short_description = 'Payment Method'
    
    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">View Receipt PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF generated"
    pdf_preview.short_description = 'PDF Preview'
    
    def has_add_permission(self, request):
        # Receipts should only be created through the API/views
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make receipts read-only in admin
        return False
    



@admin.register(ReceiptLineItem)
class ReceiptLineItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'receipt', 'quantity', 'unit_price', 'amount')
    list_filter = ('receipt',)
    search_fields = ('title', 'description', 'receipt__receipt_number')
    readonly_fields = ('amount',)
