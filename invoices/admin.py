
# invoices/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceLineItem

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1
    fields = ('title', 'description', 'quantity', 'unit_price', 'amount')
    readonly_fields = ('amount',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'quote_reference', 'user', 'total', 'payment_status_badge', 'due_date', 'created_at')
    list_filter = ('payment_status', 'issue_date', 'due_date', 'created_at')
    search_fields = ('invoice_number', 'quote__reference_number', 'user__email')
    readonly_fields = ('invoice_number', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at', 'pdf_preview', 'issue_date')
    ordering = ('-created_at',)
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'quote', 'user')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_date')
        }),
        ('Additional Info', {
            'fields': ('notes', 'pdf_file', 'pdf_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quote_reference(self, obj):
        return obj.quote.reference_number
    quote_reference.short_description = 'Quote Reference'
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'paid': '#10b981',
            'overdue': '#ef4444',
            'cancelled': '#6b7280',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_status, '#6b7280'),
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment Status'
    
    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">View Invoice PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF generated"
    pdf_preview.short_description = 'PDF Preview'
    
    actions = ['mark_as_paid', 'mark_as_overdue']
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(payment_status='pending').update(
            payment_status='paid',
            payment_date=timezone.now()
        )
        self.message_user(request, f'{updated} invoice(s) marked as paid.')
    mark_as_paid.short_description = 'Mark as Paid'
    
    def mark_as_overdue(self, request, queryset):
        updated = queryset.filter(payment_status='pending').update(payment_status='overdue')
        self.message_user(request, f'{updated} invoice(s) marked as overdue.')
    mark_as_overdue.short_description = 'Mark as Overdue'


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'invoice', 'quantity', 'unit_price', 'amount')
    list_filter = ('invoice',)
    search_fields = ('title', 'description', 'invoice__invoice_number')
    readonly_fields = ('amount',)

