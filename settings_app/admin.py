

# settings_app/admin.py
from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_email', 'company_phone', 'company_address', 'company_logo')
        }),
        ('Financial Settings', {
            'fields': ('default_tax_rate', 'currency_symbol', 'currency_code')
        }),
        ('Email Configuration', {
            'fields': ('email_footer', 'quote_email_template', 'invoice_email_template')
        }),
        ('Payment Settings', {
            'fields': ('payment_instructions', 'bank_details')
        }),
        ('Notification Settings', {
            'fields': ('admin_notification_email', 'enable_sms_notifications', 'twilio_phone_number')
        }),
        ('PDF Branding', {
            'fields': ('pdf_primary_color', 'pdf_secondary_color')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# Customize admin site
admin.site.site_header = "Quote & Invoice Management"
admin.site.site_title = "Quote System Admin"
admin.site.index_title = "Welcome to Quote & Invoice Management System"